from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import pytesseract
import io
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\terso\Desktop\GOV_USA JOBS\tesseract.exe"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

REQUIRED_WARNING = "GOVERNMENT WARNING:"
WARNING_BODY_KEYWORDS = ["according to the surgeon general", "women should not drink"]

def verify_label(text: str) -> dict:
    results = {}

    if "GOVERN" in text.upper() and "WARNING" in text.upper():
        warning_line = [line for line in text.splitlines() if REQUIRED_WARNING in line]
        body_present = any(kw in text.lower() for kw in WARNING_BODY_KEYWORDS)
        results["government_warning"] = {
            "pass": True,
            "detail": warning_line[0].strip() if warning_line else "Found",
            "note": "Warning body keywords found" if body_present else "WARNING: Body text not detected"
        }
    else:
        results["government_warning"] = {
            "pass": False,
            "detail": "GOVERNMENT WARNING: not found or not in required all-caps format"
        }

    abv_match = re.search(r'(\d{1,3}(?:\.\d+)?)\s*%', text, re.IGNORECASE)
    if abv_match:
        results["alcohol_content"] = {
            "pass": True,
            "detail": f"Found: {abv_match.group(0).strip()}"
        }
    else:
        results["alcohol_content"] = {
            "pass": False,
            "detail": "Alcohol content (e.g. '40% Alc./Vol.') not detected"
        }

    net_match = re.search(r'(\d+(?:\.\d+)?)\s*(ml|l|oz|fl oz)', text, re.IGNORECASE)
    if net_match:
        results["net_contents"] = {
            "pass": True,
            "detail": f"Found: {net_match.group(0).strip()}"
        }
    else:
        results["net_contents"] = {
            "pass": False,
            "detail": "Net contents (e.g. '750 mL') not detected"
        }

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        results["brand_name"] = {
            "pass": True,
            "detail": f"Detected first line: '{lines[0]}'"
        }
    else:
        results["brand_name"] = {
            "pass": False,
            "detail": "No text detected on label"
        }

    type_keywords = ["whiskey", "bourbon", "vodka", "rum", "gin", "tequila",
                     "wine", "beer", "ale", "lager", "brandy", "scotch", "malt"]
    type_match = next((kw for kw in type_keywords if kw in text.lower()), None)
    if type_match:
        results["class_type"] = {
            "pass": True,
            "detail": f"Detected type keyword: '{type_match}'"
        }
    else:
        results["class_type"] = {
            "pass": False,
            "detail": "No recognized class/type (e.g. Bourbon, Vodka, Wine) detected"
        }

    return results


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/upload-label/")
async def upload_label(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    text = pytesseract.image_to_string(image)

    verification = verify_label(text)
    overall_pass = all(v["pass"] for v in verification.values())

    return {
        "raw_text": text,
        "overall_result": "PASS" if overall_pass else "FAIL",
        "field_checks": verification
    }