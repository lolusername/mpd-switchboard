#!/usr/bin/env python3

import os
import argparse
import ocrmypdf
from multiprocessing import Pool, cpu_count
import tempfile
import shutil
import traceback
import json  # Added to handle JSON data

# Ensure /usr/local/bin is in the PATH (necessary for macOS and Homebrew)
os.environ["PATH"] += os.pathsep + "/usr/local/bin"

def ocr_pdf(args):
    input_pdf, output_pdf, language, in_place = args
    try:
        if in_place:
            # Create a temporary file in the same directory as the input PDF
            dir_name = os.path.dirname(input_pdf)
            with tempfile.NamedTemporaryFile(dir=dir_name, suffix=".pdf", delete=False) as temp_output:
                temp_output_pdf = temp_output.name
            try:
                ocrmypdf.ocr(
                    input_file=input_pdf,
                    output_file=temp_output_pdf,
                    language=language,
                    optimize=3,
                    deskew=True,
                    rotate_pages=True,
                    rotate_pages_threshold=15,
                    skip_text=True,
                    progress_bar=False,
                )
                # After successful processing, replace the original file
                shutil.move(temp_output_pdf, input_pdf)
                print(f"Processed (in-place): {input_pdf}")
            except Exception as e:
                # Remove temporary file if processing failed
                if os.path.exists(temp_output_pdf):
                    os.remove(temp_output_pdf)
                print(f"Failed to process {input_pdf}: {e}")
                traceback.print_exc()
        else:
            ocrmypdf.ocr(
                input_file=input_pdf,
                output_file=output_pdf,
                language=language,
                optimize=3,
                deskew=True,
                rotate_pages=True,
                rotate_pages_threshold=15,
                skip_text=True,
                progress_bar=False,
            )
            print(f"Processed: {input_pdf} -> {output_pdf}")
    except Exception as e:
        print(f"Failed to process {input_pdf}: {e}")
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="OCR unselectable PDFs")
    parser.add_argument(
        '--metadata_file', required=True, help='Path to the JSON file containing unselectable PDF paths'
    )
    parser.add_argument(
        '--output_dir', help='Directory to save the processed PDFs (ignored if --in-place is used)'
    )
    parser.add_argument(
        '--language', default='eng', help='Language(s) for OCR (default: eng)'
    )
    parser.add_argument(
        '--in-place', action='store_true', help='Replace the original PDFs in place'
    )
    args = parser.parse_args()

    metadata_file = args.metadata_file
    output_dir = args.output_dir
    language = args.language
    in_place = args.in_place

    # Read the list of PDF paths from the JSON file
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            pdf_paths = metadata.get('unselectable_pdfs', [])
    except Exception as e:
        print(f"Failed to read metadata file {metadata_file}: {e}")
        return

    if not pdf_paths:
        print(f"No unselectable PDFs found in {metadata_file}. Exiting.")
        return

    if not in_place:
        if not output_dir:
            print("Error: --output_dir is required unless --in-place is specified.")
            return
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    # Prepare arguments for multiprocessing
    ocr_args = []
    for pdf_path in pdf_paths:
        if not os.path.isfile(pdf_path):
            print(f"File not found: {pdf_path}. Skipping.")
            continue
        if in_place:
            output_pdf = None  # Not used in in-place mode
        else:
            filename = os.path.basename(pdf_path)
            output_pdf = os.path.join(output_dir, filename)
        ocr_args.append((pdf_path, output_pdf, language, in_place))

    if not ocr_args:
        print("No valid PDF files to process. Exiting.")
        return

    # Use multiprocessing to speed up processing
    pool_size = min(cpu_count(), 4)  # Limit to 4 processes to avoid overloading
    print(f"Using {pool_size} processes for OCR.")

    # For macOS, ensure 'spawn' is used and code is importable
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    with Pool(processes=pool_size) as pool:
        pool.map(ocr_pdf, ocr_args)

    print("OCR processing completed.")

if __name__ == "__main__":
    main()