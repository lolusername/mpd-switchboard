import os
from pdfminer.high_level import extract_text
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from multiprocessing import Pool, cpu_count
import sys

# -------------------------------------------------
# Setup Script Environment
# -------------------------------------------------
# Get the absolute directory where this script is located. This ensures that relative paths
# in the script behave consistently no matter where the script is executed from.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory. This helps ensure that
# any relative paths used in the script are based on the script's location, which is more
# predictable than the environment's working directory.
os.chdir(script_dir)

# Add the script's directory to the system path to make sure modules in this directory are importable.
sys.path.append(script_dir)

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

def main(pdf_dir):
    pdf_paths = []
    # Collect all PDF file paths
    for root, _, files in os.walk(pdf_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                pdf_paths.append(pdf_path)

    total_pdfs = len(pdf_paths)
    unselectable_pdfs = []

    # Use multiprocessing Pool to process PDFs in parallel
    pool_size = cpu_count()  # Use the number of CPU cores available
    print(f"Using {pool_size} processes for multiprocessing.")
    with Pool(processes=pool_size) as pool:
        # Map the is_text_selectable function to the list of PDF paths
        results = pool.map(is_text_selectable, pdf_paths)

    # Process the results
    for pdf_path, is_selectable in results:
        if not is_selectable:
            unselectable_pdfs.append(pdf_path)

    # Write the list of unselectable PDFs to a text file
    with open('unselectable_pdfs.txt', 'w', encoding='utf-8') as f:
        for pdf in unselectable_pdfs:
            f.write(pdf + '\n')

    # Calculate the percentage of unselectable PDFs
    if total_pdfs > 0:
        percent_unselectable = (len(unselectable_pdfs) / total_pdfs) * 100
    else:
        percent_unselectable = 0

    # Print the results
    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Number of unselectable PDFs: {len(unselectable_pdfs)}")
    print(f"Percentage of unselectable PDFs: {percent_unselectable:.2f}%")

if __name__ == "__main__":
    pdf_directory = '../data'  # Replace with your actual PDF directory path
    main(pdf_directory)