import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz
from google import genai

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=[""],
allow_credentials=True,
allow_methods=[""],
allow_headers=["*"],
)

client = genai.Client(
api_key=os.environ.get("GEMINI_API_KEY")
)

@app.get("/")
def home():
return {
"message": "Text2Test AI backend is running!"
}

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

@app.post("/generate-test")
async def generate_test(
pdf: UploadFile = File(...),
num_questions: int = Form(10)
):

# Giới hạn số câu từ 10 đến 40
if num_questions < 10:
    num_questions = 10

if num_questions > 40:
    num_questions = 40

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

Read the textbook content below and create exactly {num_questions}
multiple-choice questions.

Each question must have:

One clear question
Four answer choices: A, B, C, D
One correct answer

Focus on important concepts and key knowledge from the textbook.
Avoid questions about tiny or unimportant details.

Use ONLY information contained in the textbook.

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

Continue until Question {num_questions}.

Textbook content:

{text[:30000]}
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

return {
    "test": response.text,
    "num_questions": num_questions
}
