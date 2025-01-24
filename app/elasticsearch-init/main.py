import os
import sys
import argparse
import logging
from elasticsearch import Elasticsearch, helpers
from pdfminer.high_level import extract_text
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import time
from functools import partial

try:
    import boto3
    from urllib.parse import urlparse
    import tempfile
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def create_elasticsearch_index(es, index_name):
    if es.indices.exists(index=index_name):
        logging.info(f"Index '{index_name}' already exists.")
        return
    mapping = {
        "mappings": {
            "properties": {
                "title": { "type": "text" },
                "content": { "type": "text" },
                "file_path": { "type": "keyword" },
                "uploaded_at": { "type": "date" }
            }
        }
    }
    es.indices.create(index=index_name, body=mapping)
    logging.info(f"Created index '{index_name}'.")

def process_pdf_local(args):
    file_path, base_pdf_dir = args
    relative_path = os.path.relpath(file_path, base_pdf_dir)
    
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        return None
    
    doc = {
        'title': os.path.splitext(relative_path)[0],
        'content': text,
        'file_path': relative_path,
        'uploaded_at': "2024-04-27"
    }
    return doc

def process_pdf_s3(file_path):
    if not S3_AVAILABLE:
        raise ImportError("boto3 is required for S3 support")
        
    parsed = urlparse(file_path)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')
    
    s3 = boto3.client('s3')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        try:
            s3.download_file(bucket, key, tmp.name)
            text = extract_text_from_pdf(tmp.name)
        finally:
            os.unlink(tmp.name)
    
    if not text.strip():
        return None
        
    doc = {
        'title': os.path.splitext(os.path.basename(key))[0],
        'content': text,
        'file_path': file_path,
        'uploaded_at': "2024-04-27"
    }
    return doc

def list_s3_pdfs(s3_path):
    if not S3_AVAILABLE:
        raise ImportError("boto3 is required for S3 support")
        
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
                    pdf_files.append(f"s3://{bucket}/{obj['Key']}")
    
    return pdf_files

def ingest_pdfs(es, index_name, base_path):
    is_s3 = base_path.startswith('s3://')
    
    if is_s3:
        if not S3_AVAILABLE:
            raise ImportError("boto3 is required for S3 support")
        pdf_files = list_s3_pdfs(base_path)
        process_func = process_pdf_s3
        process_args = pdf_files
    else:
        pdf_files = []
        for root, _, files in os.walk(base_path):
            pdf_files.extend([os.path.join(root, f) for f in files if f.lower().endswith('.pdf')])
        process_func = process_pdf_local
        process_args = [(f, base_path) for f in pdf_files]
    
    total_files = len(pdf_files)
    logging.info(f"Found {total_files} PDF files to process.")
    
    # Process PDFs in parallel
    num_processes = max(1, cpu_count()-2)  # Ensure at least 1 process
    with Pool(processes=num_processes) as pool:
        if is_s3:
            results = list(tqdm(pool.imap(process_func, process_args), total=total_files, desc="Processing PDFs"))
        else:
            results = list(tqdm(pool.imap(process_func, process_args), total=total_files, desc="Processing PDFs"))
    
    documents = [doc for doc in results if doc is not None]
    empty_pdfs = total_files - len(documents)
    
    logging.info(f"Processed {total_files} PDFs. {empty_pdfs} were empty or failed to process.")
    
    for i in tqdm(range(0, len(documents), 1000), desc="Ingesting to Elasticsearch"):
        batch = documents[i:i+1000]
        actions = [{"_index": index_name, "_source": doc} for doc in batch]
        try:
            helpers.bulk(es, actions)
            logging.info(f"Ingested batch of {len(batch)} documents into '{index_name}'.")
        except Exception as e:
            logging.error(f"Error ingesting batch: {e}")

    logging.info(f"Ingestion complete. Total documents ingested: {len(documents)}")
    logging.info(f"Total empty PDFs skipped: {empty_pdfs}")

def main():
    parser = argparse.ArgumentParser(description="Ingest PDFs into Elasticsearch.")
    parser.add_argument('--pdf_dir', required=True, help='Base directory containing PDF files or s3:// path.')
    parser.add_argument('--index', default='pdf_documents', help='Elasticsearch index name.')
    parser.add_argument('--es_host', default='http://localhost:9200', help='Elasticsearch host URL.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.pdf_dir.startswith('s3://') and not S3_AVAILABLE:
        logging.error("S3 support requires boto3. Install it with: pip install boto3")
        sys.exit(1)

    logging.info(f"Connecting to Elasticsearch at {args.es_host}")
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            es = Elasticsearch([args.es_host], retry_on_timeout=True, max_retries=3)
            health = es.cluster.health(wait_for_status='yellow', timeout='30s')
            logging.info(f"Successfully connected to Elasticsearch at {args.es_host}")
            logging.info(f"Cluster health: {health['status']}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Failed to connect to Elasticsearch (attempt {attempt + 1}/{max_retries}): {e}")
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                logging.error(f"Cannot connect to Elasticsearch at {args.es_host} after {max_retries} attempts.")
                sys.exit(1)

    create_elasticsearch_index(es, args.index)
    
    logging.info(f"Starting PDF ingestion from: {args.pdf_dir}")
    ingest_pdfs(es, args.index, args.pdf_dir)
    logging.info("Ingestion process completed.")

if __name__ == "__main__":
    main()
