import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz
from google import genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối Gemini bằng API key đã lưu trên Render
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


@app.get("/")
def home():
    return {
        "message": "Text2Test AI backend is running!"
    }


# API upload PDF
@app.post("/upload-pdf")
async def upload_pdf(pdf: UploadFile = File(...)):
    pdf_data = await pdf.read()

    document = fitz.open(
        stream=pdf_data,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    pages = len(document)

    document.close()

    return {
        "filename": pdf.filename,
        "pages": pages,
        "text_length": len(text),
        "text": text[:5000]
    }


# API dùng Gemini để tạo đề
@app.post("/generate-test")
async def generate_test(pdf: UploadFile = File(...)):
    pdf_data = await pdf.read()

    document = fitz.open(
        stream=pdf_data,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    prompt = f"""
You are an expert test creator.

Read the textbook content below and create a test based ONLY
on the information contained in the textbook.

Create 10 multiple-choice questions.

Each question must have:
- One clear question
- Four answer choices: A, B, C, D
- One correct answer

Focus on important concepts and key knowledge.
Avoid questions about tiny or unimportant details.

Return the result in exactly this format:

Question 1: ...
A. ...
B. ...
C. ...
D. ...
Answer: A

Question 2: ...
A. ...
B. ...
C. ...
D. ...
Answer: B

Continue until Question 10.

Textbook content:

{text[:30000]}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "test": response.text
    }
