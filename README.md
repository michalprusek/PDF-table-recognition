# PDF Table Extractor

This project provides a Python-based solution for extracting tables from PDF documents and converting them into structured Excel files. It utilizes image processing techniques and OCR (Optical Character Recognition) to accurately identify and process table content.

## Features

- **PDF to Image Conversion:** Converts pages of a PDF document into images for further processing.
- **Table Detection:** Identifies table structures within the page images using image processing techniques.
- **Text Extraction:** Extracts text from the detected tables using Tesseract OCR.
- **Data Structuring:** Organizes the extracted text into structured formats resembling the original table layouts.
- **Excel Output:** Saves the structured text into Excel files, with each table's content neatly organized.

## Prerequisites

Before running this project, ensure you have the following installed:
- Python 3.x
- OpenCV (`cv2`)
- NumPy
- pandas
- PyTesseract
- pdf2image
- scikit-image
- scikit-learn
- openpyxl

Additionally, Tesseract OCR must be installed and configured on your system.

## Setup

1. Clone this repository to your local machine.
2. Install the required Python libraries by running:
   ```sh
   pip install opencv-python numpy pandas pytesseract pdf2image scikit-image scikit-learn openpyxl
3. Ensure Tesseract OCR is installed and correctly set up on your system. You might need to configure the `TESSDATA_PREFIX` environment variable in `segmentace_textu_V1.py` to point to your Tesseract data directory.

## Usage

To use this tool for extracting tables from PDF documents and converting them to Excel files, follow these steps:

1. **Prepare Your PDF Document:**
   - Place the PDF document you wish to extract tables from in the project directory.
   - By default, the script is configured to process a file named `ahc-zprava-2022.pdf`. If your document has a different name, update the `pdf_path` variable in `segmentace_textu_V1.py` accordingly.

2. **Run the Extraction Script:**
   - Open a terminal or command prompt in the project directory.
   - Execute the script by running:
     ```sh
     python segmentace_textu_V1.py
     ```
   - The script will process each page of the provided PDF document, detecting and extracting table structures and their contents.

3. **Review the Output:**
   - Upon successful execution, the script will generate Excel files corresponding to each detected table in the document. These files will be saved in the project directory, named according to the page number and table index, such as `excel/page_1_contour_1.xlsx`.
   - Additionally, for verification and review purposes, the script saves images of the processed tables and their masks in the `output` and `output_masks` directories, respectively.

4. **Adjustments and Troubleshooting:**
   - If you encounter issues with table detection or text extraction accuracy, consider adjusting the image processing parameters within the script, such as the Sauvola thresholding window size or the Gaussian Blur parameters.
   - For documents with complex layouts or non-standard table structures, manual intervention may be necessary to ensure accurate extraction.

## Advanced Configuration

- **Sauvola Thresholding:** The `sauvola_window_size` parameter can be adjusted to optimize the binary thresholding of page images, which is crucial for accurate table structure detection.
- **Mean Shift Bandwidth:** The `bandwidths` list contains the bandwidth parameters for the Mean Shift clustering algorithm, which affects how table cells are grouped into rows and columns. Experimenting with different values may yield better results for specific documents.


