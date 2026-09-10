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
# UPLOAD PDF + GENERATE TEST
# =========================

@app.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(...),
    question_count: int = Form(20),
    difficulty: str = Form("medium"),
    question_type: str = Form("multiple_choice")
):

    # -------------------------
    # Limit question number
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
    # Check PDF
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

Question
A. option
B. option
C. option
D. option
Answer: A/B/C/D
"""

    elif question_type == "true_false":

        question_instruction = f"""
Create exactly {question_count} True/False questions.

Each question must contain:

Question
A. True
B. False
Answer: A/B
"""

    else:

        question_instruction = f"""
Create exactly {question_count} short-answer questions.

Each question must contain:

Question
Answer: ...
"""


    # -------------------------
    # Difficulty
    # -------------------------

    difficulty_instruction = {
        "easy": "Make the questions easy and test basic understanding.",
        "medium": "Make the questions moderately challenging and test understanding and application.",
        "hard": "Make the questions challenging. Require deeper understanding, comparison, reasoning, or application of concepts."
    }.get(
        difficulty,
        "Make the questions moderately challenging."
    )


    # -------------------------
    # Prompt
    # -------------------------

    prompt = f"""

You are an expert educational test creator.

Your task is to create a test from the textbook content below.

IMPORTANT RULES:

1. Use ONLY information contained in the textbook.
2. Do not invent facts that are not in the textbook.
3. Do not use outside knowledge.
4. Avoid extremely minor details.
5. Focus on important concepts and key knowledge.
6. All questions and answers must be written in ENGLISH.
7. Create exactly {question_count} questions.
8. Difficulty: {difficulty}.
9. {difficulty_instruction}

{question_instruction}

Return the questions in a clean format.

For multiple choice, use exactly:

Question 1: ...
A. ...
B. ...
C. ...
D. ...
Answer: B

Question 2: ...
A. ...
B. ...
C. ...
D. ...
Answer: A

Continue until Question {question_count}.

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
