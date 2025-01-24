import os
import pandas as pd
from pdfminer.high_level import extract_text
from tqdm import tqdm
import argparse
import logging
import pickle
from multiprocessing import Pool, cpu_count

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_text(text):
    """
    Sanitize the extracted text while preserving important symbols.
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # You can add more sanitization steps here if needed
    return text

def extract_pdf_text(pdf_path):
    """
    Extract text from a PDF file.
    """
    try:
        text = extract_text(pdf_path)
        return sanitize_text(text)
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def process_single_pdf(args):
    full_path, input_folder = args
    text = extract_pdf_text(full_path)
    if text:
        return {'full_path': full_path, 'text': text}
    return None

def process_pdfs(input_folder):
    """
    Process all PDFs in the input folder and create a DataFrame.
    """
    pdf_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append((full_path, input_folder))
    
    pool_size = max(1, cpu_count() - 2)  # Ensure at least 1 process
    with Pool(processes=pool_size) as pool:
        results = list(tqdm(pool.imap(process_single_pdf, pdf_files), total=len(pdf_files), desc="Processing PDFs"))
    
    data = [result for result in results if result is not None]
    return pd.DataFrame(data)

def save_dataframe(df, output_file):
    """
    Save the DataFrame using pickle for efficient storage and retrieval.
    """
    with open(output_file, 'wb') as f:
        pickle.dump(df, f)
    logging.info(f"DataFrame saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Create a DataFrame from PDF documents")
    parser.add_argument('--input_folder', required=True, help='Path to the folder containing PDFs')
    parser.add_argument('--output_file', required=True, help='Path to save the output DataFrame')
    args = parser.parse_args()

    logging.info("Starting PDF processing")
    df = process_pdfs(args.input_folder)
    
    logging.info(f"Created DataFrame with {len(df)} documents")
    
    save_dataframe(df, args.output_file)
    
    logging.info("Processing completed")

if __name__ == "__main__":
    main()
