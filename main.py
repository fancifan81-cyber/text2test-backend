import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz
from google import genai


app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# GEMINI
# =========================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "Text2Test AI backend is running!"
    }


# =========================
# GENERATE TEST
# =========================

@app.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(...),
    question_count: int = Form(20),
    difficulty: str = Form("medium"),
    question_type: str = Form("multiple_choice"),
):

    # -------------------------
    # Limit number of questions
    # -------------------------

    if question_count < 10:
        question_count = 10

    if question_count > 40:
        question_count = 40


    # -------------------------
    # Read PDF
    # -------------------------

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


    # -------------------------
    # Check PDF text
    # -------------------------

    if not text.strip():
        return {
            "success": False,
            "message": "Could not extract text from this PDF."
        }


    # -------------------------
    # Question type
    # -------------------------

    if question_type == "multiple_choice":

        question_instruction = f"""
Create exactly {question_count} multiple-choice questions.

Each question must contain:

Question 1: ...
A. ...
B. ...
C. ...
D. ...
Answer: A

Use four answer choices for every question.
Only one answer should be correct.
"""

    elif question_type == "true_false":

        question_instruction = f"""
Create exactly {question_count} True/False questions.

Each question must contain:

Question 1: ...
A. True
B. False
Answer: A

Only one answer should be correct.
"""

    else:

        question_instruction = f"""
Create exactly {question_count} short-answer questions.

Each question must contain:

Question 1: ...
Answer: ...

The answer should be concise and directly supported by the textbook.
"""


    # -------------------------
    # Difficulty
    # -------------------------

    difficulty_instruction = {
        "easy":
            "Make the questions easy and test basic understanding.",

        "medium":
            "Make the questions moderately challenging and test understanding and application.",

        "hard":
            "Make the questions challenging and require deeper understanding, comparison, reasoning, or application of concepts."
    }.get(
        difficulty,
        "Make the questions moderately challenging."
    )


    # -------------------------
    # Prompt
    # -------------------------

    prompt = f"""
You are an expert educational test creator.

Your task is to create a test based ONLY on the textbook content provided below.

IMPORTANT RULES:

1. Use ONLY information contained in the textbook.
2. Do NOT invent facts.
3. Do NOT use outside knowledge.
4. Focus on important concepts and key knowledge.
5. Avoid questions about extremely minor details.
6. All questions must be written in ENGLISH.
7. All answers must be written in ENGLISH.
8. Create EXACTLY {question_count} questions.
9. Difficulty level: {difficulty}.
10. {difficulty_instruction}

QUESTION TYPE:

{question_instruction}

IMPORTANT:

Follow the requested format exactly.

Do not add introductions.

Do not add explanations before the test.

Do not add explanations after the test.

TEXTBOOK CONTENT:

{text[:30000]}
"""


    # -------------------------
    # Gemini
    # -------------------------

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    # -------------------------
    # Return result
    # -------------------------

    return {
        "success": True,
        "filename": pdf.filename,
        "pages": pages,
        "num_questions": question_count,
        "difficulty": difficulty,
        "question_type": question_type,
        "language": "english",
        "test": response.text
    }
