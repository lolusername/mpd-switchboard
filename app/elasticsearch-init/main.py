import os
import sys
import argparse
import logging
from elasticsearch import Elasticsearch, helpers
from pdfminer.high_level import extract_text
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

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

def process_pdf(args):
    file_path, base_pdf_dir = args
    relative_path = os.path.relpath(file_path, base_pdf_dir)
    
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        return None
    
    doc = {
        'title': os.path.splitext(relative_path)[0],
        'content': text,
        'file_path': relative_path,
        'uploaded_at': "2024-04-27"  # You may want to modify this
    }
    return doc

def ingest_pdfs(es, index_name, base_pdf_dir):
    pdf_files = []
    for root, _, files in os.walk(base_pdf_dir):
        pdf_files.extend([os.path.join(root, f) for f in files if f.lower().endswith('.pdf')])
    
    total_files = len(pdf_files)
    logging.info(f"Found {total_files} PDF files to process.")

    process_args = [(f, base_pdf_dir) for f in pdf_files]
    
    with Pool(processes=cpu_count()-2) as pool:
        results = list(tqdm(pool.imap(process_pdf, process_args), total=total_files, desc="Processing PDFs"))
    
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
    parser.add_argument('--pdf_dir', required=True, help='Base directory containing PDF files.')
    parser.add_argument('--index', default='pdf_documents', help='Elasticsearch index name.')
    parser.add_argument('--es_host', default='http://localhost:9200', help='Elasticsearch host URL.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info(f"Connecting to Elasticsearch at {args.es_host}")
    es = Elasticsearch([args.es_host])

    if not es.ping():
        logging.error(f"Cannot connect to Elasticsearch at {args.es_host}. Make sure it's running.")
        sys.exit(1)
    else:
        logging.info(f"Successfully connected to Elasticsearch at {args.es_host}")

    create_elasticsearch_index(es, args.index)
    
    logging.info(f"Starting PDF ingestion from directory: {args.pdf_dir}")
    ingest_pdfs(es, args.index, args.pdf_dir)
    logging.info("Ingestion process completed.")

if __name__ == "__main__":
    main()
