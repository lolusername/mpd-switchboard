import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from fpdf import FPDF

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


# -------------------------------------------------
# Utility Functions
# -------------------------------------------------

def get_pdf_size(file_path):
    """
    Get the size of a PDF file in megabytes (MB).
    
    Parameters:
    - file_path (str): Path to the PDF file
    
    Returns:
    - float: File size in MB, or None if an error occurs
    """
    try:
        # os.path.getsize() returns the size of the file in bytes, so we convert to MB.
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert from bytes to MB
        return file_size
    except Exception as e:
        # If an error occurs (e.g., file is not found), print the error message.
        print(f"Error getting size for {file_path}: {e}")
        return None


def get_pdf_files(input_folder):
    """
    Recursively find all PDF files in the specified folder.
    
    Parameters:
    - input_folder (str): Path to the folder to search for PDFs
    
    Returns:
    - list: List of file paths to PDFs found in the folder
    """
    pdf_files = []
    
    # os.walk generates the file names in a directory tree, walking from the root down.
    # It traverses through each folder and subfolder.
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            # Only add files that end with ".pdf" (case insensitive check)
            if file_name.lower().endswith('.pdf'):
                # Join the directory and file name to form the full file path
                file_path = os.path.join(root, file_name)
                pdf_files.append(file_path)
    return pdf_files


def get_pdf_sizes_concurrently(pdf_files, max_workers=8):
    """
    Get the sizes of PDF files concurrently using threading.
    
    This function uses a thread pool to calculate the size of multiple PDFs concurrently,
    which improves performance by taking advantage of I/O-bound tasks (reading file sizes).
    
    Parameters:
    - pdf_files (list): List of file paths to PDFs
    - max_workers (int): Maximum number of threads to use (default is 8)
    
    Returns:
    - list: List of tuples (file_path, size_in_MB)
    """
    pdf_sizes = []
    
    # ThreadPoolExecutor is used to execute tasks concurrently. It's particularly useful for I/O-bound tasks.
    # We specify the number of threads with max_workers. The default is 8, but this can be adjusted based on system resources.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit each PDF file to be processed by the executor. This returns a Future object that will hold the result.
        futures = {executor.submit(get_pdf_size, pdf_file): pdf_file for pdf_file in pdf_files}
        
        # as_completed yields results as they are completed by the workers.
        for future in as_completed(futures):
            pdf_file = futures[future]
            try:
                # Get the result from the future (the size of the PDF in MB)
                size = future.result()
                if size is not None:
                    # Save the file path and size as a tuple
                    pdf_sizes.append((pdf_file, size))
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
    
    return pdf_sizes


# -------------------------------------------------
# Visualization Functions
# -------------------------------------------------

def generate_combined_chart(pdf_data):
    """
    Generate a combined chart (linear and logarithmic) of PDF file sizes.
    
    Parameters:
    - pdf_data (list): List of tuples (file_path, size_in_MB)
    
    Returns:
    - str: Path to the generated chart image
    """
    if not pdf_data:
        print("No PDFs found.")
        return None

    # Unpack file paths and file sizes from the pdf_data list
    pdf_files, pdf_sizes = zip(*pdf_data)

    # Categorize files based on their sizes
    small_files = [size for size in pdf_sizes if size < 1]  # Files < 1 MB
    medium_files = [size for size in pdf_sizes if 1 <= size <= 10]  # Files between 1-10 MB
    large_files = [size for size in pdf_sizes if size > 10]  # Files > 10 MB

    # Define categories for the bar chart and count how many files fall into each category
    categories = ['< 1 MB (Small)', '1-10 MB (Medium)', '> 10 MB (Large)']
    counts = [len(small_files), len(medium_files), len(large_files)]

    # Create a figure with 2 subplots (1 for linear scale, 1 for log scale)
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Bar plot (Linear scale)
    axs[0].bar(categories, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    axs[0].set_title('PDF File Size Distribution (Linear Scale)', fontsize=14)
    axs[0].set_xlabel('File Size Categories', fontsize=12)
    axs[0].set_ylabel('Number of PDFs', fontsize=12)

    # Bar plot (Logarithmic scale)
    axs[1].bar(categories, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    axs[1].set_yscale('log')  # Logarithmic y-axis for better visualization of size differences
    axs[1].set_title('PDF File Size Distribution (Log Scale)', fontsize=14)
    axs[1].set_xlabel('File Size Categories', fontsize=12)
    axs[1].set_ylabel('Number of PDFs', fontsize=12)

    # Adjust layout to ensure subplots don't overlap
    plt.tight_layout()

    # Save the combined plot to a PNG file
    chart_path = os.path.join(script_dir, "reports/assets/pdf_size_distribution_combined.png")
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# -------------------------------------------------
# PDF Report Generation
# -------------------------------------------------

def generate_pdf_report(min_size, max_size, median_size, total_size, total_files, combined_chart_img_path, output_pdf):
    """
    Generate a PDF report with file size statistics and the combined chart.
    
    Parameters:
    - min_size (float): Minimum file size in MB
    - max_size (float): Maximum file size in MB
    - median_size (float): Median file size in MB
    - total_size (float): Total size of all PDFs in MB
    - total_files (int): Total number of PDF files
    - combined_chart_img_path (str): Path to the combined chart image
    - output_pdf (str): Path to the output PDF file
    """
    # Create a new PDF document using FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'PDF Size Distribution Report', ln=True, align='C')

    # Add Summary Information
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f'Total Number of PDFs: {total_files}', ln=True)
    pdf.cell(200, 10, f'Total Size of PDFs: {total_size/1000:.2f} GB', ln=True)  # Convert to GB for readability
    pdf.ln(2)
    
    # Draw a horizontal line to separate summary from detailed stats
    pdf.set_draw_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Add detailed statistics
    pdf.cell(200, 10, f'Minimum PDF Size: {min_size:.2f} MB', ln=True)
    pdf.cell(200, 10, f'Maximum PDF Size: {max_size:.2f} MB', ln=True)
    pdf.cell(200, 10, f'Median PDF Size: {median_size:.2f} MB', ln=True)
    pdf.ln(10)

       # Insert the combined chart (linear and log scale on the same page)
    pdf.cell(200, 10, 'File Size Distribution (Linear and Log Scale):', ln=True)
    pdf.image(combined_chart_img_path, x=10, y=None, w=pdf.w - 20)

    # Save the generated PDF to the output path
    pdf.output(output_pdf)


# -------------------------------------------------
# Main Function (Entry Point)
# -------------------------------------------------

def main():
    """
    Main function that orchestrates the entire PDF report generation process.
    
    1. Finds all PDFs in the specified folder.
    2. Calculates the size of each PDF concurrently.
    3. Generates a chart (linear and log scale) of file size distribution.
    4. Creates a PDF report with statistics and the chart.
    """
    # Path to the folder containing PDFs (update this as per your environment)
    input_folder = '../data'  # Update this to your folder path

    # Retrieve a list of all PDF files in the directory
    pdf_files = get_pdf_files(input_folder)

    # Get the size of each PDF file concurrently to optimize performance
    pdf_data = get_pdf_sizes_concurrently(pdf_files, max_workers=os.cpu_count())

    # Generate a combined chart (both linear and log scale in one image) for visualization
    combined_chart_img_path = generate_combined_chart(pdf_data)

    # If no PDFs are found or something goes wrong, terminate early
    if not combined_chart_img_path:
        print("No valid PDFs found or chart generation failed.")
        return

    # Calculate key statistics for the report
    pdf_files, pdf_sizes = zip(*pdf_data)
    min_size = min(pdf_sizes)  # Minimum size of the PDFs
    max_size = max(pdf_sizes)  # Maximum size of the PDFs
    median_size = np.median(pdf_sizes)  # Median size of the PDFs
    total_size = np.sum(pdf_sizes)  # Total size of all PDFs (in MB)
    total_files = len(pdf_sizes)  # Total number of PDF files

    # Generate the final PDF report with all the calculated statistics and the chart
    output_pdf_path = os.path.join(script_dir, "reports/pdf_report_with_combined_visuals.pdf")
    generate_pdf_report(min_size, max_size, median_size, total_size, total_files, combined_chart_img_path, output_pdf_path)

    print(f"PDF report generated successfully: {output_pdf_path}")


# -------------------------------------------------
# Run the Script
# -------------------------------------------------

if __name__ == "__main__":
    # This block ensures the script runs only when executed directly, not when imported as a module
    main()