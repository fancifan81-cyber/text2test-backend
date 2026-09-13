import os
import json
import re

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import fitz

from google import genai
from supabase import create_client, Client


# =========================================================
# CONFIG
# =========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")

# Prefer the service-role key for backend database operations.
# If it does not exist, fall back to SUPABASE_KEY.
SUPABASE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY"
) or os.environ.get("SUPABASE_KEY")


# =========================================================
# APP
# =========================================================

app = FastAPI()


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CLIENTS
# =========================================================

gemini_client = None
supabase: Client = None


if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Text2Test AI backend is running!"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "success": True,
        "gemini_configured": bool(GEMINI_API_KEY),
        "supabase_configured": bool(
            SUPABASE_URL and SUPABASE_KEY
        ),
        "model": GEMINI_MODEL
    }


# =========================================================
# EXTRACT PDF TEXT
# =========================================================

def extract_pdf_text(pdf_data: bytes):
    document = fitz.open(
        stream=pdf_data,
        filetype="pdf"
    )

    pages = len(document)

    text_parts = []

    for page in document:
        page_text = page.get_text()

        if page_text:
            text_parts.append(page_text)

    document.close()

    full_text = "\n".join(text_parts).strip()

    return full_text, pages


# =========================================================
# CLEAN AI RESPONSE
# =========================================================

def clean_ai_response(text: str):
    if not text:
        return ""

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # Sometimes Gemini returns extra text before/after JSON.
    # Try to extract the JSON object.
    if not text.startswith("{"):
        start = text.find("{")

        if start >= 0:
            text = text[start:]

    if not text.endswith("}"):
        end = text.rfind("}")

        if end >= 0:
            text = text[:end + 1]

    return text.strip()


# =========================================================
# NORMALIZE QUESTION
# =========================================================

def normalize_question(q):
    if not isinstance(q, dict):
        return None

    question = str(
        q.get("question", "")
    ).strip()

    if not question:
        return None

    answer = str(
        q.get("answer", "")
    ).strip()

    question_type = str(
        q.get("question_type", "")
    ).strip().lower()

    difficulty = str(
        q.get("difficulty", "")
    ).strip().lower()

    topic = str(
        q.get("topic", "")
    ).strip()

    options = q.get("options", {})

    if not isinstance(options, dict):
        options = {}

    normalized_options = {}

    for key, value in options.items():

        letter = str(key).strip().upper()

        if letter in ["A", "B", "C", "D", "E"]:
            normalized_options[letter] = str(
                value
            ).strip()

    # Default question type
    if question_type not in [
        "multiple_choice",
        "true_false",
        "short_answer"
    ]:
        if normalized_options:
            question_type = "multiple_choice"
        else:
            question_type = "short_answer"

    # Default difficulty
    if difficulty not in [
        "easy",
        "medium",
        "hard"
    ]:
        difficulty = "medium"

    return {
        "question": question,
        "options": normalized_options,
        "answer": answer,
        "question_type": question_type,
        "difficulty": difficulty,
        "topic": topic
    }


# =========================================================
# GENERATE QUESTIONS
# =========================================================

def generate_questions(
    textbook_text: str,
    question_count: int,
    difficulty: str,
    question_type: str
):

    if not gemini_client:
        raise Exception(
            "GEMINI_API_KEY is not configured on Render."
        )

    # Keep the PDF from becoming excessively large.
    # This still gives Gemini a large amount of textbook content.
    max_chars = 100000

    if len(textbook_text) > max_chars:
        textbook_text = textbook_text[:max_chars]

    if question_type == "multiple_choice":

        type_instruction = """
Create multiple-choice questions.

Each question must have exactly four options:
A, B, C, D.

The answer field must contain only one letter:
A, B, C, or D.
"""

    elif question_type == "true_false":

        type_instruction = """
Create True/False questions.

Each question must have exactly two options:

A: True
B: False

The answer field must contain only:
A or B.
"""

    else:

        type_instruction = """
Create short-answer questions.

The options object must be empty.

The answer field must contain the correct short answer.
"""


    prompt = f"""
You are an expert educational test generator.

Read the textbook content below and create exactly
{question_count} high-quality questions.

Difficulty:
{difficulty}

Question type:
{question_type}

{type_instruction}

IMPORTANT RULES:

1. Use ONLY information supported by the textbook.
2. Do not invent facts that are not in the textbook.
3. Avoid duplicate questions.
4. Questions should cover different parts and topics of the textbook.
5. Make the questions educational and clear.
6. Do not include explanations.
7. Return ONLY valid JSON.
8. Do not use Markdown.
9. The JSON must follow this exact structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "answer": "A",
      "question_type": "multiple_choice",
      "difficulty": "{difficulty}",
      "topic": "Topic name"
    }}
  ]
}}

For True/False:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "True",
        "B": "False"
      }},
      "answer": "A",
      "question_type": "true_false",
      "difficulty": "{difficulty}",
      "topic": "Topic name"
    }}
  ]
}}

For Short Answer:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{}},
      "answer": "Correct answer",
      "question_type": "short_answer",
      "difficulty": "{difficulty}",
      "topic": "Topic name"
    }}
  ]
}}

TEXTBOOK CONTENT:

{textbook_text}
"""


    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    raw_response = getattr(
        response,
        "text",
        ""
    )

    cleaned = clean_ai_response(
        raw_response
    )

    if not cleaned:
        raise Exception(
            "Gemini returned an empty response."
        )

    try:

        data = json.loads(cleaned)

    except Exception as error:

        raise Exception(
            "Could not parse Gemini JSON response: "
            + str(error)
        )

    if not isinstance(data, dict):
        raise Exception(
            "Gemini returned an invalid JSON object."
        )

    raw_questions = data.get(
        "questions",
        []
    )

    if not isinstance(raw_questions, list):
        raise Exception(
            "Gemini response does not contain a valid questions list."
        )

    final_questions = []

    for q in raw_questions:

        normalized = normalize_question(q)

        if normalized:
            final_questions.append(
                normalized
            )

    if not final_questions:
        raise Exception(
            "Gemini did not generate any valid questions."
        )

    return final_questions


# =========================================================
# UPLOAD PDF + GENERATE TEST
# =========================================================

@app.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(...),
    question_count: int = Form(20),
    difficulty: str = Form("medium"),
    question_type: str = Form("multiple_choice")
):

    try:

        # -------------------------------------------------
        # Validate file
        # -------------------------------------------------

        if not pdf.filename:
            return {
                "success": False,
                "error": "No PDF file was uploaded."
            }

        if not pdf.filename.lower().endswith(".pdf"):
            return {
                "success": False,
                "error": "Please upload a PDF file."
            }


        # -------------------------------------------------
        # Validate question count
        # -------------------------------------------------

        question_count = max(
            10,
            min(question_count, 40)
        )


        # -------------------------------------------------
        # Validate difficulty
        # -------------------------------------------------

        difficulty = difficulty.lower().strip()

        if difficulty not in [
            "easy",
            "medium",
            "hard"
        ]:

            difficulty = "medium"


        # -------------------------------------------------
        # Validate question type
        # -------------------------------------------------

        question_type = question_type.lower().strip()

        if question_type not in [
            "multiple_choice",
            "true_false",
            "short_answer"
        ]:

            question_type = "multiple_choice"


        # -------------------------------------------------
        # Read PDF
        # -------------------------------------------------

        pdf_data = await pdf.read()

        if not pdf_data:
            return {
                "success": False,
                "error": "The uploaded PDF is empty."
            }


        # -------------------------------------------------
        # Extract text
        # -------------------------------------------------

        textbook_text, pages = extract_pdf_text(
            pdf_data
        )

        if not textbook_text:
            return {
                "success": False,
                "error": (
                    "Could not extract text from the PDF. "
                    "The PDF may contain scanned images only."
                )
            }


        # -------------------------------------------------
        # Generate questions
        # -------------------------------------------------

        questions = generate_questions(
            textbook_text,
            question_count,
            difficulty,
            question_type
        )


        # -------------------------------------------------
        # Return to frontend
        # -------------------------------------------------

        return {
            "success": True,
            "filename": pdf.filename,
            "pages": pages,
            "text_length": len(textbook_text),
            "difficulty": difficulty,
            "question_type": question_type,
            "question_count": len(questions),
            "questions": questions
        }


    except Exception as error:

        print(
            "UPLOAD / GENERATE ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


# =========================================================
# SAVE EXAM + QUESTIONS
# =========================================================

@app.post("/save-exam")
async def save_exam(data: dict):

    try:

        if not supabase:
            return {
                "success": False,
                "error": (
                    "Supabase is not configured. "
                    "Please check SUPABASE_URL and "
                    "SUPABASE_KEY / SUPABASE_SERVICE_ROLE_KEY."
                )
            }


        # -------------------------------------------------
        # Get exam data
        # -------------------------------------------------

        title = str(
            data.get("title", "")
        ).strip()

        subject_id = data.get(
            "subject_id"
        )

        grade = data.get(
            "grade"
        )

        topic = str(
            data.get("topic", "")
        ).strip()

        exam_type = str(
            data.get("exam_type", "")
        ).strip()

        year = data.get(
            "year"
        )

        description = str(
            data.get("description", "")
        ).strip()

        file_url = str(
            data.get("file_url", "")
        ).strip()

        answer_url = str(
            data.get("answer_url", "")
        ).strip()

        difficulty = str(
            data.get("difficulty", "medium")
        ).strip()

        question_type = str(
            data.get(
                "question_type",
                "multiple_choice"
            )
        ).strip()

        questions = data.get(
            "questions",
            []
        )


        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not title:
            return {
                "success": False,
                "error": "Exam title is required."
            }

        if subject_id is None:
            return {
                "success": False,
                "error": "Subject is required."
            }

        try:
            subject_id = int(subject_id)

        except Exception:
            return {
                "success": False,
                "error": "Invalid subject_id."
            }


        if not isinstance(questions, list):
            return {
                "success": False,
                "error": "Questions must be a list."
            }


        if len(questions) == 0:
            return {
                "success": False,
                "error": "There are no questions to save."
            }


        # -------------------------------------------------
        # IMPORTANT:
        # Validate subject using ONLY id.
        #
        # We intentionally do NOT select "name".
        #
        # This prevents:
        # subjects_1.name does not exist
        #
        # when the actual column is "Name".
        # -------------------------------------------------

        subject_check = (
            supabase
            .table("subjects")
            .select("id")
            .eq("id", subject_id)
            .limit(1)
            .execute()
        )


        if not subject_check.data:
            return {
                "success": False,
                "error": (
                    "The selected subject does not exist "
                    "in the subjects table."
                )
            }


        # -------------------------------------------------
        # Prepare exam
        # -------------------------------------------------

        exam_row = {
            "title": title,
            "subject_id": subject_id,
            "grade": grade if grade else None,
            "topic": topic if topic else None,
            "exam_type": exam_type if exam_type else None,
            "year": year,
            "description": (
                description
                if description
                else None
            ),
            "file_url": (
                file_url
                if file_url
                else None
            ),
            "answer_url": (
                answer_url
                if answer_url
                else None
            ),
            "difficulty": difficulty,
            "question_type": question_type
        }


        # -------------------------------------------------
        # Insert exam
        # -------------------------------------------------

        exam_response = (
            supabase
            .table("exams")
            .insert(exam_row)
            .execute()
        )


        if not exam_response.data:
            return {
                "success": False,
                "error": "Exam could not be inserted."
            }


        exam = exam_response.data[0]

        exam_id = exam.get("id")


        if exam_id is None:
            return {
                "success": False,
                "error": (
                    "Exam was created but no exam ID "
                    "was returned."
                )
            }


        # -------------------------------------------------
        # Prepare questions
        # -------------------------------------------------

        question_rows = []


        for q in questions:

            normalized = normalize_question(q)

            if not normalized:
                continue


            options = normalized["options"]


            question_row = {
                "exam_id": exam_id,

                "question":
                    normalized["question"],

                "options":
                    options,

                "answer":
                    normalized["answer"],

                "question_type":
                    normalized["question_type"],

                "difficulty":
                    normalized["difficulty"],

                "topic":
                    normalized["topic"]
                    if normalized["topic"]
                    else None
            }


            question_rows.append(
                question_row
            )


        if not question_rows:

            # Try to remove the empty exam
            try:

                (
                    supabase
                    .table("exams")
                    .delete()
                    .eq("id", exam_id)
                    .execute()
                )

            except Exception:
                pass


            return {
                "success": False,
                "error": (
                    "No valid questions were available "
                    "to save."
                )
            }


        # -------------------------------------------------
        # Insert questions
        # -------------------------------------------------

        question_response = (
            supabase
            .table("questions")
            .insert(question_rows)
            .execute()
        )


        if not question_response.data:

            return {
                "success": False,
                "error": (
                    "Exam was created, but questions "
                    "could not be saved."
                ),
                "exam_id": exam_id
            }


        # -------------------------------------------------
        # Success
        # -------------------------------------------------

        return {
            "success": True,
            "exam_id": exam_id,
            "questions_saved": len(
                question_response.data
            ),
            "message": (
                "Exam and questions saved successfully!"
            )
        }


    except Exception as error:

        print(
            "SAVE EXAM ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


# =========================================================
# END
# =========================================================
