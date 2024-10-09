# Pre-Processing and Exploration of PDF Document Dataset

## Overview

As part of building a **data dashboard app** for a nonprofit organization, this phase involves **pre-processing** and **exploring** a collection of PDF documents. This step is crucial because it helps us understand the structure and size of the documents in the dataset, allowing us to manage them more efficiently in the app.

The pre-processing work ensures that we can **organize**, **upload**, and **store** these documents in a way that makes them easily accessible and usable by the nonprofit team and stakeholders. By analyzing the dataset now, we avoid potential technical challenges later, ensuring the app runs smoothly and cost-effectively.

## Scripts and Their Functions

### 1. doc-size-analysis.py

This script analyzes the size distribution of PDF files in a given directory.

Main functions:
- `get_pdf_size`: Calculates the size of a PDF file in megabytes.
- `get_pdf_files`: Recursively finds all PDF files in a specified folder.
- `get_pdf_sizes_concurrently`: Gets the sizes of PDF files concurrently using threading.
- `generate_combined_chart`: Creates a combined chart (linear and logarithmic) of PDF file sizes.
- `generate_pdf_report`: Generates a PDF report with file size statistics and the combined chart.

### 2. ocr-check.py

This script checks whether PDFs in a given directory have selectable text or require OCR.

Main functions:
- `is_text_selectable`: Checks if a PDF has selectable text.
- `main`: Processes all PDFs in the input folder, checks for text selectability, and generates a metadata JSON file with the results.

### 3. run-ocr.py

This script performs OCR on PDFs that were identified as not having selectable text.

Main functions:
- `ocr_pdf`: Applies OCR to a single PDF file.
- `main`: Reads the metadata JSON file, processes the unselectable PDFs with OCR, and optionally replaces the original files.

## Why Pre-Processing Matters

When dealing with large numbers of documents, such as **reports**, **case studies**, or **legal files**, it is important to understand their size and structure. This helps us:

- **Store documents efficiently**: Cloud storage providers, like **AWS**, often have different storage tiers. By understanding the size of the files, we can make better decisions about which storage options to choose, keeping costs down without sacrificing performance.
  
- **Ensure quick access**: Knowing the size of the documents means we can ensure that the data dashboard allows users to **quickly retrieve** and view the files, without long delays.

- **Prepare for future scalability**: As the nonprofit organization grows, the number of documents will likely increase. Pre-processing ensures the system can handle larger datasets in the future.

## What Does Pre-Processing Involve?

In this phase, we focus on the following key tasks:

1. **Analyzing File Sizes**:
   - We calculate the size of each PDF document in **megabytes (MB)**. This helps us understand how much storage space is required and whether there are any particularly large files that might require special attention.
   
2. **Visualizing the Data**:
   - We create **charts** that show the distribution of file sizes. This allows us to easily see how many small, medium, or large files exist in the dataset.
   
   - We use both **linear** and **logarithmic** charts to show this. The linear chart provides a straightforward view, while the logarithmic chart helps us understand how a few very large files compare to the rest of the dataset.
   
3. **Checking for OCR Requirements**:
   - We analyze each PDF to determine if it has selectable text or requires OCR processing.
   
4. **Applying OCR When Necessary**:
   - For documents identified as needing OCR, we process them to make the text selectable and searchable.

5. **Generating a Summary Report**:
   - We generate a **PDF report** that summarizes the dataset. This report includes:
     - The **total number of files**.
     - The **total size of all the files** combined.
     - The **smallest** and **largest** file sizes.
     - The **median** (middle value) file size, which gives us a sense of what a typical document looks like.
     - The **charts** showing the distribution of file sizes.
     - Information on the number of files requiring OCR processing.
   - This report can be shared with team members and stakeholders to give them an overview of the dataset.

## Summary of the Process

1. **Collect**: We first collect all the PDFs from your document archive and prepare them for analysis.
   
2. **Analyze**: We analyze each document’s size, creating a full picture of the dataset’s structure.

3. **Visualize**: We produce charts that show how the document sizes are distributed, helping us see if there are any unusual files or patterns.

4. **Report**: Finally, we generate a report that summarizes all of this information, giving both the technical team and the nonprofit’s leadership an overview of what the dataset looks like.

