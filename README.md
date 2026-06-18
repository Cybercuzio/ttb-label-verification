# TTB Alcohol Label Verification App

An AI-powered web application that verifies alcohol labels meet TTB (Alcohol and Tobacco Tax and Trade Bureau) compliance requirements.

## Live Demo
https://ttb-label-verification-ktwp.onrender.com

## Approach
The app uses Google's Gemini multimodal AI model to analyze uploaded label images directly, extracting and verifying the presence of required TTB fields without relying on traditional OCR. This approach was chosen after an initial attempt with Tesseract OCR proved unreliable on photographed labels and could not be deployed on Render's free tier due to system dependency restrictions.

## Tools & Technologies
- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **AI Model:** Google Gemini (gemini-2.5-flash) for image analysis and field extraction
- **Hosting:** Render (free tier)

## Fields Verified
- Brand Name
- Class/Type designation
- Alcohol Content (ABV)
- Net Contents
- Government Warning Statement (including all-caps format check)

## Setup Instructions
1. Install Python 3.x
2. Clone this repository
3. Install dependencies: `pip install -r requirements.txt`
4. Obtain a free Gemini API key from https://aistudio.google.com/apikey
5. Set the environment variable `GEMINI_API_KEY` with your key
6. Run the server: `uvicorn main:app --reload`
7. Open browser at `http://127.0.0.1:8000`

## Assumptions & Trade-offs
- This is a prototype and is not integrated with the COLA system
- Field detection accuracy depends on image clarity; well-lit, in-focus label photos produce the most reliable results
- The Government Warning check verifies both presence and correct all-caps formatting of the header text
- No persistent storage or database is used; each upload is processed independently