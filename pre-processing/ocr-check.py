#!/usr/bin/env python3

import os
import json
import argparse
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from multiprocessing import Pool, cpu_count

def is_text_selectable(pdf_path):
    try:
        # Extract text from the first page to improve performance
        text = extract_text(pdf_path, maxpages=1)
        if text and any(char.isalnum() for char in text):
            return (pdf_path, True)
        else:
            return (pdf_path, False)
    except PDFTextExtractionNotAllowed:
        # Text extraction is not allowed (e.g., encrypted PDF)
        return (pdf_path, False)
    except Exception as e:
        # Handle other exceptions (e.g., corrupted PDF)
        print(f"Error processing {pdf_path}: {e}")
        return (pdf_path, False)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Analyze PDFs for text selectability")
    parser.add_argument('--input_folder', required=True, help='Path to the folder containing PDFs')
    parser.add_argument('--output_dir', required=True, help='Directory to save the output files')
    args = parser.parse_args()

    input_folder = args.input_folder
    output_dir = args.output_dir

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    pdf_paths = []
    # Collect all PDF file paths
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                pdf_paths.append(pdf_path)

    total_pdfs = len(pdf_paths)
    unselectable_pdfs = []

    # Use multiprocessing Pool to process PDFs in parallel
    pool_size = max(1, cpu_count() - 2)  # Ensure at least 1 process
    print(f"Using {pool_size} processes for multiprocessing.")
    with Pool(processes=pool_size) as pool:
        # Map the is_text_selectable function to the list of PDF paths
        results = pool.map(is_text_selectable, pdf_paths)

    # Process the results
    for pdf_path, is_selectable in results:
        if not is_selectable:
            unselectable_pdfs.append(pdf_path)

    # Calculate the percentage of unselectable PDFs
    percentage_unselectable = (len(unselectable_pdfs) / total_pdfs) * 100 if total_pdfs > 0 else 0

    # Prepare metadata dictionary
    metadata = {
        'total_pdfs': total_pdfs,
        'number_unselectable_pdfs': len(unselectable_pdfs),
        'percentage_unselectable': percentage_unselectable,
        'unselectable_pdfs': unselectable_pdfs
    }

    # Write the metadata to a JSON file
    output_file_path = os.path.join(output_dir, 'meta_data.json')
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

    # Print the results
    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Number of unselectable PDFs: {len(unselectable_pdfs)}")
    print(f"Percentage of unselectable PDFs: {percentage_unselectable:.2f}%")
    print(f"Metadata saved to: {output_file_path}")

if __name__ == "__main__":
    main()