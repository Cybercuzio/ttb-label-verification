from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import anthropic
import base64
import re
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

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/upload-label/")
async def upload_label(file: UploadFile = File(...)):
    image_data = await file.read()
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")
    content_type = file.content_type or "image/jpeg"

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": content_type,
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Analyze this alcohol label image and extract the following fields. 
                        For each field, state whether it is present or not.
                        Respond in this exact format:
                        BRAND_NAME: <value or NOT FOUND>
                        CLASS_TYPE: <value or NOT FOUND>
                        ALCOHOL_CONTENT: <value or NOT FOUND>
                        NET_CONTENTS: <value or NOT FOUND>
                        GOVERNMENT_WARNING: <PRESENT or NOT FOUND>
                        WARNING_FORMAT_CORRECT: <YES if 'GOVERNMENT WARNING:' appears in all caps, NO otherwise>"""
                    }
                ],
            }
        ],
    )

    response_text = message.content[0].text
    lines = response_text.strip().split('\n')
    parsed = {}
    for line in lines:
        if ':' in line:
            key, _, value = line.partition(':')
            parsed[key.strip()] = value.strip()

    field_checks = {
        "brand_name": {
            "pass": parsed.get("BRAND_NAME", "NOT FOUND")