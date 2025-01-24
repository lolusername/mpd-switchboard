import logging
import argparse
from elasticsearch import Elasticsearch
import os
import boto3
from urllib.parse import urlparse
import tempfile
from pdfminer.high_level import extract_text
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool
from multiprocessing import cpu_count

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def connect_to_elasticsearch(es_host):
    logging.info(f"Connecting to Elasticsearch at {es_host}")
    es = Elasticsearch([es_host])
    
    # Wait for yellow status
    health = es.cluster.health(wait_for_status='yellow', timeout='30s')
    logging.info(f"Successfully connected to Elasticsearch at {es_host}")
    logging.info(f"Cluster health: {health['status']}")
    
    return es

def create_index_if_not_exists(es, index_name):
    if es.indices.exists(index=index_name):
        logging.info(f"Index '{index_name}' already exists.")
        return

    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "filename": {"type": "keyword"},
                "path": {"type": "keyword"},
                "title": {"type": "text"},
                "author": {"type": "text"},
                "creation_date": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
                "last_modified": {"type": "date", "format": "strict_date_optional_time||epoch_millis"}
            }
        }
    }
    
    es.indices.create(index=index_name, body=settings)
    logging.info(f"Created index '{index_name}'")

def list_s3_pdfs(s3_path):
    parsed = urlparse(s3_path)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/')
    
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    
    pdf_files = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                if obj['Key'].lower().endswith('.pdf'):
                    pdf_files.append((bucket, obj['Key']))
    
    logging.info(f"Found {len(pdf_files)} PDF files to process.")
    return pdf_files

def process_pdf(args):
    bucket, key, es_host, index_name = args
    try:
        s3 = boto3.client('s3')
        es = Elasticsearch([es_host])
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            logging.info(f"Downloading s3://{bucket}/{key} to {tmp_file.name}")
            s3.download_file(bucket, key, tmp_file.name)
            
            # Extract text from PDF
            text = extract_text(tmp_file.name)
            
            # Index the document
            doc = {
                'content': text,
                'filename': os.path.basename(key),
                'path': f"s3://{bucket}/{key}"
            }
            es.index(index=index_name, document=doc)
            logging.info(f"Indexed {key}")
            
            # Clean up
            os.unlink(tmp_file.name)
            return True, key
            
    except Exception as e:
        logging.error(f"Error processing {key}: {str(e)}")
        return False, key

def ingest_pdfs(es, index_name, base_path):
    if base_path.startswith('s3://'):
        # S3 path
        bucket = base_path.split('/')[2]
        prefix = '/'.join(base_path.split('/')[3:])
        s3 = boto3.client('s3')
        pdfs = list_s3_pdfs(s3, bucket, prefix)
        logging.info(f"Found {len(pdfs)} PDF files to process.")
        
        # Use max(1, cpu_count()-2) to ensure at least 1 process
        with Pool(processes=max(1, cpu_count()-2)) as pool:
            args = [(s3, bucket, pdf, es, index_name) for pdf in pdfs]
            results = pool.starmap(process_pdf, args)
            
            successful = sum(1 for r in results if r)
            logging.info(f"Successfully processed {successful} out of {len(pdfs)} PDFs")
    else:
        logging.error("Only S3 paths are supported")
        return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_dir', required=True, help='S3 path containing PDF files')
    parser.add_argument('--index', default='pdf_documents', help='Elasticsearch index name')
    parser.add_argument('--es_host', default='http://localhost:9200', help='Elasticsearch host')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--workers', type=int, default=4, help='Number of worker processes')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    es = connect_to_elasticsearch(args.es_host)
    create_index_if_not_exists(es, args.index)
    ingest_pdfs(es, args.index, args.pdf_dir)

if __name__ == '__main__':
    main() 