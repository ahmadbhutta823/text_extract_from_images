# Text Extraction from Images

This Python script extracts text from images using Optical Character Recognition (OCR) and saves the results to text files.

## Prerequisites

1. Python 3.7 or higher
2. Tesseract OCR engine must be installed on your system:
   - **Windows**: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

## Installation

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure Tesseract is properly installed and accessible from your system PATH.

## Usage

1. Place your images in the `images` directory.
2. Run the script:
   ```bash
   python text_extractor.py
   ```

## Output

The script will create two files in the `extracted_text` directory:

1. `extracted_text_[timestamp].txt`: Contains the full extracted text from all images
2. `summary_[timestamp].txt`: Contains a summary of the extraction process with word counts and text previews

## Features

- Processes multiple image formats (JPG, JPEG, PNG, BMP, TIFF)
- Cleans and formats extracted text
- Creates detailed extraction reports
- Handles errors gracefully
- Generates both full text and summary reports

## Supported Image Types

- JPG/JPEG
- PNG
- BMP
- TIFF

## Error Handling

The script includes error handling for:
- Missing image files
- Invalid image formats
- OCR processing errors

## Notes

- The quality of text extraction depends on the image quality and clarity
- For best results, ensure images are clear and well-lit
- Text should be clearly visible and properly oriented