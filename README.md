 # TTB Alcohol Label Verification App

An AI-powered web application that verifies alcohol labels meet TTB (Alcohol and Tobacco Tax and Trade Bureau) compliance requirements.

## Approach
The app uses OCR (Tesseract via pytesseract) to extract text from uploaded label images and checks for the presence and format of required TTB fields.

## Tools & Technologies
- **Backend:** Python, FastAPI, pytesseract, Pillow
- **Frontend:** HTML, CSS, JavaScript
- **OCR Engine:** Tesseract

## Fields Verified
- Government Warning Statement
- Alcohol Content (ABV)
- Net Contents
- Brand Name
- Class/Type

## Setup Instructions
1. Install Python 3.x
2. Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
3. Clone this repository
4. Install dependencies: `pip install -r requirements.txt`
5. Update the Tesseract path in `main.py` to match your installation
6. Run the server: `uvicorn main:app --reload`
7. Open browser at `http://127.0.0.1:8000`

## Assumptions & Trade-offs
- OCR accuracy depends on image quality; clearer images produce better results
- Government Warning detection uses keyword matching on extracted text
- This is a prototype and not integrated with the COLA system
