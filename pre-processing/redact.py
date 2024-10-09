#!/usr/bin/env python3

import os
import argparse
import logging
from multiprocessing import Pool, cpu_count
import spacy
from pdfminer.high_level import extract_text
from tqdm import tqdm
import fitz  # PyMuPDF
import re
import sys
from contextlib import contextmanager

# Ensure the 'reports' directory exists
LOG_DIR = '../reports'
os.makedirs(LOG_DIR, exist_ok=True)

# Initialize logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'sensitive_data_log.txt'),
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def load_spacy_model():
    """
    Load the SpaCy model with POS tagging to ensure lemmatizer works correctly.

    Returns:
        spacy.language.Language: Loaded SpaCy model.
    """
    model_name = "en_core_web_sm"
    try:
        nlp = spacy.load(model_name)
    except OSError:
        logging.info(f"SpaCy model '{model_name}' not found. Downloading now...")
        from spacy.cli import download
        download(model_name)
        nlp = spacy.load(model_name)
    return nlp

# Load SpaCy model globally to avoid reloading in each worker
nlp = load_spacy_model()

# Compile regex patterns once
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_REGEX = re.compile(
    r'(?<!\d)'                             # Negative lookbehind to ensure the previous character isn't a digit
    r'(?:\+?(\d{1,3})\s?)?'                # Optional country code
    r'(?:\(?\d{3}\)?[\s\.-]?)'             # Area code with optional parentheses and separators
    r'\d{3}[\s\.-]?\d{4}'                   # Local number
    r'(?!\d)'                               # Negative lookahead to ensure the next character isn't a digit
)

def extract_sensitive_data(text):
    """
    Extract full names, email addresses, and phone numbers from the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary containing lists of full names, emails, and phone numbers.
    """
    sensitive_data = {
        'full_names': [],
        'emails': [],
        'phone_numbers': []
    }

    # Extract emails
    emails = EMAIL_REGEX.findall(text)
    sensitive_data['emails'] = emails

    # Extract phone numbers
    phones = PHONE_REGEX.findall(text)
    phone_numbers = set()
    for match in PHONE_REGEX.finditer(text):
        phone = match.group()
        digits = re.sub(r'\D', '', phone)  # Remove non-digit characters
        if len(digits) >= 10:
            phone_numbers.add(phone)
    sensitive_data['phone_numbers'] = list(phone_numbers)

    # Extract full names using SpaCy's NER
    doc = nlp(text)
    full_names = set()
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            full_names.add(ent.text)
    sensitive_data['full_names'] = list(full_names)

    return sensitive_data

@contextmanager
def suppress_stderr():
    """
    A context manager to suppress stderr within its block.
    Redirects stderr to os.devnull.
    """
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def redact_pdf(pdf_path, output_pdf_path, dry_run):
    """
    Redact sensitive full names, email addresses, and phone numbers from a PDF.

    Args:
        pdf_path (str): Path to the input PDF.
        output_pdf_path (str): Path to save the redacted PDF.
        dry_run (bool): If True, log sensitive data without modifying the PDF.

    Returns:
        dict: Status of the redaction process.
    """
    try:
        # Open the PDF using PyMuPDF within the suppress_stderr context
        with suppress_stderr():
            doc = fitz.open(pdf_path)
        redacted_items = {'full_names': [], 'emails': [], 'phone_numbers': []}

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Extract text from the current page
            text = page.get_text()

            # Extract sensitive data from the page
            sensitive_data = extract_sensitive_data(text)

            if dry_run:
                # Log sensitive data without modifying the PDF
                if sensitive_data['full_names']:
                    logging.info(f"Full Names in {pdf_path}, Page {page_num + 1}: {sensitive_data['full_names']}")
                if sensitive_data['emails']:
                    logging.info(f"Emails in {pdf_path}, Page {page_num + 1}: {sensitive_data['emails']}")
                if sensitive_data['phone_numbers']:
                    logging.info(f"Phone Numbers in {pdf_path}, Page {page_num + 1}: {sensitive_data['phone_numbers']}")
                if not (sensitive_data['full_names'] or sensitive_data['emails'] or sensitive_data['phone_numbers']):
                    logging.info(f"No sensitive data found in {pdf_path}, Page {page_num + 1}.")
                continue  # Skip redaction in dry-run mode

            if sensitive_data['full_names'] or sensitive_data['emails'] or sensitive_data['phone_numbers']:
                # Redact full names
                for name in sensitive_data['full_names']:
                    with suppress_stderr():
                        text_instances = page.search_for(name, quads=True)
                    for inst in text_instances:
                        page.add_redact_annot(inst.rect, fill=(0, 0, 0))
                        redacted_items['full_names'].append(name)

                # Redact emails
                for email in sensitive_data['emails']:
                    with suppress_stderr():
                        text_instances = page.search_for(email, quads=True)
                    for inst in text_instances:
                        page.add_redact_annot(inst.rect, fill=(0, 0, 0))
                        redacted_items['emails'].append(email)

                # Redact phone numbers
                for phone in sensitive_data['phone_numbers']:
                    with suppress_stderr():
                        text_instances = page.search_for(phone, quads=True)
                    for inst in text_instances:
                        page.add_redact_annot(inst.rect, fill=(0, 0, 0))
                        redacted_items['phone_numbers'].append(phone)

        if not dry_run:
            with suppress_stderr():
                # Apply all redactions
                doc.apply_redactions()
                doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
            doc.close()

            if any(redacted_items.values()):
                return {'pdf_path': pdf_path, 'status': 'success', 'redacted_items': redacted_items}
            else:
                # No sensitive data found; copy the original PDF
                with open(pdf_path, 'rb') as src, open(output_pdf_path, 'wb') as dst:
                    dst.write(src.read())
                doc.close()
                return {'pdf_path': pdf_path, 'status': 'no_sensitive_data', 'redacted_items': redacted_items}
        else:
            return {'pdf_path': pdf_path, 'status': 'success', 'redacted_items': redacted_items}

    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}", exc_info=True)
        return {'pdf_path': pdf_path, 'status': 'error', 'error': str(e)}

def process_pdfs(input_folder, output_folder, dry_run, log_file):
    """
    Process all PDFs in the input folder for redaction.

    Args:
        input_folder (str): Directory containing input PDFs.
        output_folder (str): Directory to save redacted PDFs.
        dry_run (bool): If True, perform a dry run without saving redacted PDFs.
        log_file (str): Path to the log file.
    """
    # Ensure output directory exists
    if not dry_run:
        os.makedirs(output_folder, exist_ok=True)

    # Gather all PDF paths
    pdf_paths = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                relative_path = os.path.relpath(pdf_path, input_folder)
                output_pdf_path = os.path.join(output_folder, relative_path)
                output_pdf_dir = os.path.dirname(output_pdf_path)
                if not dry_run:
                    os.makedirs(output_pdf_dir, exist_ok=True)
                pdf_paths.append((pdf_path, output_pdf_path, dry_run))

    total_pdfs = len(pdf_paths)
    print(f"Found {total_pdfs} PDFs to process.")

    pool_size = cpu_count() - 2 # leave 2 cores free for other tasks
    print(f"Using {pool_size} processes for multiprocessing.")

    with Pool(processes=pool_size) as pool:
        results = list(tqdm(pool.starmap(redact_pdf, pdf_paths), total=total_pdfs))

    # Summary of results
    success_count = sum(1 for result in results if result['status'] == 'success')
    no_data_count = sum(1 for result in results if result['status'] == 'no_sensitive_data')
    error_count = sum(1 for result in results if result['status'] == 'error')
    redacted_items_count = {
        'full_names': sum(len(result.get('redacted_items', {}).get('full_names', [])) for result in results if result['status'] == 'success'),
        'emails': sum(len(result.get('redacted_items', {}).get('emails', [])) for result in results if result['status'] == 'success'),
        'phone_numbers': sum(len(result.get('redacted_items', {}).get('phone_numbers', [])) for result in results if result['status'] == 'success')
    }

    print(f"Redaction completed. Success: {success_count}, No Sensitive Data: {no_data_count}, Errors: {error_count}")
    print(f"Total full names redacted: {redacted_items_count['full_names']}")
    print(f"Total email addresses redacted: {redacted_items_count['emails']}")
    print(f"Total phone numbers redacted: {redacted_items_count['phone_numbers']}")
    if not dry_run:
        print(f"Redacted PDFs saved to {output_folder}")
    else:
        print(f"Dry-run completed. Sensitive data logged to {os.path.join(LOG_DIR, 'sensitive_data_log.txt')}")
        
def main():
    """
    Main function to parse arguments and initiate the PDF redaction process.
    """
    parser = argparse.ArgumentParser(description="Redact sensitive data from PDFs.")
    parser.add_argument('--input_folder', required=True, help='Path to input PDFs folder.')
    parser.add_argument('--output_folder', required=True, help='Path to output redacted PDFs folder.')
    parser.add_argument('--dry_run', action='store_true', help='Run in dry-run mode.')
    parser.add_argument('--log_file', default='reports/sensitive_data_log.txt', help='Path to the log file for dry-run mode.')
    args = parser.parse_args()

    # Update logging configuration if log_file is provided
    if args.dry_run:
        logging.info("Running in dry-run mode. No PDFs will be modified.")

    process_pdfs(args.input_folder, args.output_folder, args.dry_run, args.log_file)

if __name__ == "__main__":
    main()