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
