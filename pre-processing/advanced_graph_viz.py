import os
import networkx as nx
import spacy
from pathlib import Path
from pdfminer.high_level import extract_text
from tqdm import tqdm
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from functools import partial
import numpy as np
from joblib import Parallel, delayed
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import json
import logging
from itertools import groupby
import psutil
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_optimal_batch_sizes():
    """Calculate optimal batch sizes based on system resources"""
    total_memory = psutil.virtual_memory().total / (1024 ** 3)  # Total memory in GB
    available_cores = cpu_count()
    
    # Calculate different batch sizes for different operations
    sizes = {
        'pdf_batch': min(int(total_memory * 2), 200),  # PDF processing batch size
        'text_chunk': 50000,  # Characters per text chunk
        'nlp_batch': min(int(available_cores * 1.5), 20),  # NLP processing batch
        'extraction_batch': min(available_cores * 2, 30)  # Entity extraction batch
    }
    
    logger.info(f"Optimized batch sizes: {sizes}")
    return sizes


class PDFProcessor:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        logger.info("Initializing PDF Processor...")
        self.pdf_files = list(Path(input_dir).rglob("*.pdf"))
        logger.info(f"Found {len(self.pdf_files)} PDF files")
        
        # Get optimal batch sizes
        self.batch_sizes = get_optimal_batch_sizes()
        self.n_jobs = max(1, cpu_count() - 1)
        
        # Initialize spaCy
        logger.info("Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
        self.nlp.max_length = 3000000  # Increase limit
        # Load NER separately with smaller chunks
        self.ner = spacy.load("en_core_web_sm", disable=['parser'])
        self.ner.max_length = 100000
        
    def clean_text(self, text):
        """Clean extracted text"""
        # Replace multiple newlines and spaces
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        return text.strip()
        
    def extract_text(self, file_path):
        """Extract and clean text from PDF"""
        try:
            output = StringIO()
            with open(file_path, 'rb') as file:
                extract_text_to_fp(file, output, laparams=LAParams())
                text = output.getvalue()
            
            # Clean the text
            text = self.clean_text(text)
            
            # Debug output
            if not hasattr(self, 'text_debug_count'):
                self.text_debug_count = 0
            if self.text_debug_count < 3:
                logger.info(f"\nExtracted text from {file_path}:")
                logger.info(f"Text length: {len(text)}")
                if text:
                    logger.info(f"Sample: {text[:200]}")
                self.text_debug_count += 1
            
            return text if text else None
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return None
            
    def extract_keywords(self, text, nlp, ner):
        """Extract keywords from text using chunks for large documents"""
        keywords = set()
        
        # Split text into chunks of 90k characters
        chunk_size = 90000
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        for chunk in chunks:
            # Process with base NLP
            doc = nlp(chunk)
            
            # Get important words
            important_words = [token.text.lower() for token in doc 
                             if token.pos_ in {'NOUN', 'PROPN', 'ADJ'} 
                             and not token.is_stop 
                             and len(token.text) > 3]
            keywords.update(important_words)
            
            # Process with NER
            ner_doc = ner(chunk)
            entity_keywords = [ent.text.lower() for ent in ner_doc.ents 
                             if len(ent.text) > 3]
            keywords.update(entity_keywords)
        
        # Clean and filter keywords
        clean_keywords = set()
        for kw in keywords:
            clean_kw = self.clean_text(kw)
            if clean_kw and len(clean_kw) > 3 and len(clean_kw.split()) <= 3:
                clean_keywords.add(clean_kw)
        
        return sorted(list(clean_keywords), key=len, reverse=True)
        
    def process_document(self, file_path):
        """Process a single document"""
        try:
            # Extract and clean text
            text = self.extract_text(file_path)
            if not text:
                return None
                
            # Debug first few documents
            if not hasattr(self, 'doc_debug_count'):
                self.doc_debug_count = 0
            if self.doc_debug_count < 3:
                logger.info(f"\nProcessing document: {file_path}")
                logger.info(f"Text length: {len(text)}")
                logger.info(f"Sample text: {text[:200]}")
            
            # Extract keywords
            keywords = self.extract_keywords(text, self.nlp, self.ner)
            
            # Debug output
            if self.doc_debug_count < 3:
                logger.info(f"Total keywords found: {len(keywords)}")
                if keywords:
                    logger.info(f"Sample keywords: {keywords[:10]}")
                self.doc_debug_count += 1
            
            if not keywords:
                return None
                
            return {
                'path': file_path,
                'entities': [],  # Skip entities for now
                'relations': [],  # Skip relations
                'keywords': keywords[:50]  # Limit to top 50 keywords
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None

    def process_pdf_batch(self, pdf_paths):
        """Process a batch of PDFs"""
        logger.info(f"Starting batch with {len(pdf_paths)} PDFs")
        texts = []
        for pdf_path in pdf_paths:
            try:
                text = self.extract_text_from_pdf(pdf_path)
                if text:
                    texts.append((str(pdf_path), text))  # Convert PosixPath to string
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {str(e)}")

        results = []
        for pdf_path, text in texts:
            try:
                # Process text with spaCy
                doc = self.nlp(text)

                # Extract information
                entities = []
                relations = []
                keywords = []

                # Entity extraction
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'GPE', 'FACILITY', 'PRODUCT', 'EVENT']:
                        entities.append((ent.text, ent.label_))

                # Relation extraction
                for token in doc:
                    if token.dep_ in ('nsubj', 'dobj') and token.head.pos_ == 'VERB':
                        subject = token.text
                        verb = token.head.text
                        obj = [w for w in token.head.children if w.dep_ == 'dobj']
                        if obj:
                            relations.append((subject, verb, obj[0].text))

                # Keyword extraction
                keywords = [token.lemma_.lower() for token in doc
                            if not token.is_stop and token.is_alpha
                            and len(token.text) > 2]

                results.append({
                    'path': pdf_path,  # Already converted to string
                    'entities': entities,
                    'relations': relations,
                    'keywords': keywords
                })

            except Exception as e:
                logger.error(f"Failed to process document {pdf_path}: {str(e)}")

        logger.info(f"Completed batch processing of {len(results)} documents")
        return results

    def process_all_documents(self):
        """Process all PDF documents using parallel processing"""
        logger.info(f"Processing {len(self.pdf_files)} PDF files...")
        
        # Initialize NLP models here
        nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
        nlp.max_length = 3000000
        ner = spacy.load("en_core_web_sm", disable=['parser'])
        ner.max_length = 100000
        
        # Process in batches
        batch_size = self.batch_sizes['pdf_batch']
        processed_docs = []
        
        # Create batches
        batches = [
            self.pdf_files[i:i + batch_size] 
            for i in range(0, len(self.pdf_files), batch_size)
        ]
        
        # Process each batch with parallel text extraction
        for batch_idx, batch in enumerate(tqdm(batches, desc="Processing batches")):
            try:
                # Extract text in parallel
                with ThreadPoolExecutor(max_workers=self.n_jobs * 2) as executor:
                    future_to_file = {
                        executor.submit(self.extract_text, str(pdf)): pdf 
                        for pdf in batch
                    }
                    
                    # Collect text extraction results
                    texts = {}
                    for future in concurrent.futures.as_completed(future_to_file):
                        pdf = future_to_file[future]
                        try:
                            text = future.result()
                            if text:
                                texts[pdf] = text
                        except Exception as e:
                            logger.error(f"Text extraction failed for {pdf}: {str(e)}")
                
                # Process texts with NLP in parallel using joblib
                if texts:
                    # Process in smaller chunks for memory efficiency
                    chunk_size = self.batch_sizes['nlp_batch']
                    text_items = list(texts.items())
                    chunks = [
                        text_items[i:i + chunk_size] 
                        for i in range(0, len(text_items), chunk_size)
                    ]
                    
                    for chunk in chunks:
                        # Process chunk in parallel
                        chunk_results = Parallel(n_jobs=self.n_jobs)(
                            delayed(self.process_text)(pdf, text, nlp, ner) 
                            for pdf, text in chunk
                        )
                        processed_docs.extend([r for r in chunk_results if r])
                
                # Debug output for first batch
                if batch_idx == 0:
                    logger.info(f"\nFirst batch results:")
                    logger.info(f"Processed {len(batch)} files")
                    logger.info(f"Got {len(processed_docs)} valid results")
                    if processed_docs:
                        for doc in processed_docs[:3]:
                            logger.info(f"\nFile: {doc['path']}")
                            logger.info(f"Keywords: {doc['keywords']}")
                            
            except Exception as e:
                logger.error(f"Batch {batch_idx} failed: {str(e)}")
        
        return processed_docs

    def process_text(self, pdf_path, text, nlp, ner):
        """Process extracted text with NLP"""
        try:
            # Extract keywords using provided NLP models
            keywords = self.extract_keywords(text, nlp, ner)
            
            if not keywords:
                return None
                
            return {
                'path': str(pdf_path),
                'entities': [],  # Skip entities for now
                'relations': [],  # Skip relations
                'keywords': keywords[:50]  # Limit to top 50 keywords
            }
            
        except Exception as e:
            logger.error(f"Text processing failed for {pdf_path}: {str(e)}")
            return None


def main(input_dir, output_dir):
    """Main execution function"""
    logger.info("Starting main execution...")
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    
    # Process PDFs
    processor = PDFProcessor(input_dir)
    processed_docs = processor.process_all_documents()
    
    if not processed_docs:
        logger.error("No documents were processed successfully")
        return
    
    # Validate and clean processed docs
    valid_docs = []
    for doc in processed_docs:
        if doc and doc.get('keywords') and any(k.strip() for k in doc['keywords']):
            valid_docs.append(doc)
    
    logger.info(f"Found {len(valid_docs)} documents with valid keywords")
    
    # Save results
    try:
        output_path = os.path.join(output_dir, 'processed_docs.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(valid_docs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed documents saved to {output_path}")
        logger.info(f"Successfully processed {len(valid_docs)} documents")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create graph visualizations from PDF documents")
    parser.add_argument("--input_dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output_dir", required=True, help="Directory to save visualizations")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir)
