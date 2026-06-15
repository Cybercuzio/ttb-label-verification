from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import PIL.Image
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

PROMPT = (
    "Analyze this alcohol label image and extract the following fields. "
    "For each field, state whether it is present or not. "
    "Respond in this exact format with no extra text:\n"
    "BRAND_NAME: <value or NOT FOUND>\n"
    "CLASS_TYPE: <value or NOT FOUND>\n"
    "ALCOHOL_CONTENT: <value or NOT FOUND>\n"
    "NET_CONTENTS: <value or NOT FOUND>\n"
    "GOVERNMENT_WARNING: <PRESENT or NOT FOUND>\n"
    "WARNING_FORMAT_CORRECT: <YES if GOVERNMENT WARNING appears in all caps, NO otherwise>"
)

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/upload-label/")
async def upload_label(file: UploadFile = File(...)):
    image_data = await file.read()
    image = PIL.Image.open(io.BytesIO(image_data))

    response = model.generate_content([image, PROMPT])
    response_text = response.text
    lines = response_text.strip().split('\n')
    parsed = {}
    for line in lines:
        if ':' in line:
            key, _, value = line.partition(':')
            parsed[key.strip()] = value.strip()

    field_checks = {
        "brand_name": {
            "pass": parsed.get("BRAND_NAME", "NOT FOUND") != "NOT FOUND",
            "detail": parsed.get("BRAND_NAME", "Not detected")
        },
        "class_type": {
            "pass": parsed.get("CLASS_TYPE", "NOT FOUND") != "NOT FOUND",
            "detail": parsed.get("CLASS_TYPE", "Not detected")
        },
        "alcohol_content": {
            "pass": parsed.get("ALCOHOL_CONTENT", "NOT FOUND") != "NOT FOUND",
            "detail": parsed.get("ALCOHOL_CONTENT", "Not detected")
        },
        "net_contents": {
            "pass": parsed.get("NET_CONTENTS", "NOT FOUND") != "NOT FOUND",
            "detail": parsed.get("NET_CONTENTS", "Not detected")
        },
        "government_warning": {
            "pass": parsed.get("GOVERNMENT_WARNING", "NOT FOUND") == "PRESENT" and parsed.get("WARNING_FORMAT_CORRECT", "NO") == "YES",
            "detail": "Government Warning present and correctly formatted" if parsed.get("GOVERNMENT_WARNING") == "PRESENT" else "Government Warning not found"
        }
    }

    overall_pass = all(v["pass"] for v in field_checks.values())

    return {
        "overall_result": "PASS" if overall_pass else "FAIL",
        "field_checks": field_checks
    }