import os
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from fpdf import FPDF
import argparse

# -------------------------------------------------
# Utility Functions
# -------------------------------------------------

def get_pdf_size(file_path):
    """
    Get the size of a PDF file in megabytes (MB).
    """
    try:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
        return file_size
    except Exception as e:
        print(f"Error getting size for {file_path}: {e}")
        return None

def get_pdf_files(input_folder):
    """
    Recursively find all PDF files in the specified folder.
    """
    pdf_files = []
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            if file_name.lower().endswith('.pdf'):
                file_path = os.path.join(root, file_name)
                pdf_files.append(file_path)
    return pdf_files

def get_pdf_sizes_concurrently(pdf_files, max_workers=8):
    """
    Get the sizes of PDF files concurrently using threading.
    """
    pdf_sizes = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_pdf_size, pdf_file): pdf_file for pdf_file in pdf_files}
        for future in as_completed(futures):
            pdf_file = futures[future]
            try:
                size = future.result()
                if size is not None:
                    pdf_sizes.append((pdf_file, size))
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
    return pdf_sizes

# -------------------------------------------------
# Visualization Functions
# -------------------------------------------------

def generate_combined_chart(pdf_data, output_dir):
    """
    Generate a combined chart (linear and logarithmic) of PDF file sizes.
    """
    if not pdf_data:
        print("No PDFs found.")
        return None

    pdf_files, pdf_sizes = zip(*pdf_data)

    # Categorize files based on their sizes
    small_files = [size for size in pdf_sizes if size < 1]  # Files < 1 MB
    medium_files = [size for size in pdf_sizes if 1 <= size <= 10]  # Files between 1-10 MB
    large_files = [size for size in pdf_sizes if size > 10]  # Files > 10 MB

    # Define categories and counts
    categories = ['< 1 MB (Small)', '1-10 MB (Medium)', '> 10 MB (Large)']
    counts = [len(small_files), len(medium_files), len(large_files)]

    # Create figure with subplots
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Linear scale bar plot
    axs[0].bar(categories, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    axs[0].set_title('PDF File Size Distribution (Linear Scale)', fontsize=14)
    axs[0].set_xlabel('File Size Categories', fontsize=12)
    axs[0].set_ylabel('Number of PDFs', fontsize=12)

    # Log scale bar plot
    axs[1].bar(categories, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    axs[1].set_yscale('log')
    axs[1].set_title('PDF File Size Distribution (Log Scale)', fontsize=14)
    axs[1].set_xlabel('File Size Categories', fontsize=12)
    axs[1].set_ylabel('Number of PDFs', fontsize=12)

    plt.tight_layout()

    # Save the combined plot
    # Create the assets subdirectory inside output_dir
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    chart_path = os.path.join(assets_dir, "pdf_size_distribution_combined.png")
    plt.savefig(chart_path)
    plt.close()

    return chart_path

# -------------------------------------------------
# PDF Report Generation
# -------------------------------------------------

def generate_pdf_report(min_size, max_size, median_size, total_size, total_files, combined_chart_img_path, output_pdf):
    """
    Generate a PDF report with file size statistics and the combined chart.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'PDF Size Distribution Report', ln=True, align='C')

    # Summary Information
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f'Total Number of PDFs: {total_files}', ln=True)
    pdf.cell(200, 10, f'Total Size of PDFs: {total_size/1024:.2f} GB', ln=True)  # Convert to GB
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.cell(200, 10, f'Minimum PDF Size: {min_size:.2f} MB', ln=True)
    pdf.cell(200, 10, f'Maximum PDF Size: {max_size:.2f} MB', ln=True)
    pdf.cell(200, 10, f'Median PDF Size: {median_size:.2f} MB', ln=True)
    pdf.ln(10)

    # Insert combined chart
    pdf.cell(200, 10, 'File Size Distribution (Linear and Log Scale):', ln=True)
    pdf.image(combined_chart_img_path, x=10, y=None, w=pdf.w - 20)

    # Save the PDF report
    pdf.output(output_pdf)

# -------------------------------------------------
# Main Function (Entry Point)
# -------------------------------------------------

def main():
    """
    Main function that orchestrates the entire PDF report generation process.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate PDF Size Distribution Report")
    parser.add_argument('--input_folder', required=True, help='Path to the folder containing PDFs')
    parser.add_argument('--output_dir', required=True, help='Directory to save the output files')
    args = parser.parse_args()

    input_folder = args.input_folder
    output_dir = args.output_dir

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Retrieve all PDF files
    pdf_files = get_pdf_files(input_folder)

    # Get sizes concurrently
    pdf_data = get_pdf_sizes_concurrently(pdf_files, max_workers=os.cpu_count())

    # Generate combined chart
    combined_chart_img_path = generate_combined_chart(pdf_data, output_dir)

    if not combined_chart_img_path:
        print("No valid PDFs found or chart generation failed.")
        return

    # Calculate statistics
    pdf_files, pdf_sizes = zip(*pdf_data)
    min_size = min(pdf_sizes)
    max_size = max(pdf_sizes)
    median_size = np.median(pdf_sizes)
    total_size = np.sum(pdf_sizes)
    total_files = len(pdf_sizes)

    # Generate PDF report
    output_pdf_path = os.path.join(output_dir, "pdf_report_with_combined_visuals.pdf")
    generate_pdf_report(min_size, max_size, median_size, total_size, total_files, combined_chart_img_path, output_pdf_path)

    print(f"PDF report generated successfully: {output_pdf_path}")

# -------------------------------------------------
# Run the Script
# -------------------------------------------------

if __name__ == "__main__":
    main()