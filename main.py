import os
import json
import time

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import fitz

from google import genai
from supabase import create_client


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
# ENVIRONMENT VARIABLES
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# =========================================================
# GEMINI CLIENT
# =========================================================

gemini_client = None

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# SUPABASE CLIENT
# =========================================================

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Text2Test AI backend is running!"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "success": True,
        "gemini_configured": gemini_client is not None,
        "supabase_configured": supabase is not None
    }


# =========================================================
# TEST SUPABASE
# =========================================================

@app.get("/test-supabase")
def test_supabase():

    if supabase is None:
        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    try:

        response = (
            supabase
            .table("subjects")
            .select("id, Name")
            .order("id")
            .execute()
        )

        return {
            "success": True,
            "subjects": response.data or []
        }

    except Exception as error:

        print(
            "SUPABASE TEST ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


# =========================================================
# GET SUBJECTS
# =========================================================

@app.get("/subjects")
def get_subjects():

    if supabase is None:
        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    try:

        response = (
            supabase
            .table("subjects")
            .select("id, Name")
            .order("id")
            .execute()
        )

        subjects = []

        for row in response.data or []:

            subjects.append({
                "id": row.get("id"),
                "name": row.get("Name")
            })

        return {
            "success": True,
            "subjects": subjects
        }

    except Exception as error:

        print(
            "GET SUBJECTS ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


# =========================================================
# GEMINI GENERATION
# =========================================================

def generate_with_gemini(prompt):

    if gemini_client is None:
        raise Exception(
            "GEMINI_API_KEY is not configured."
        )

    models = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite"
    ]

    last_error = None

    for model in models:

        for attempt in range(2):

            try:

                print(
                    f"GEMINI ATTEMPT: "
                    f"model={model}, "
                    f"attempt={attempt + 1}"
                )

                response = (
                    gemini_client
                    .models
                    .generate_content(
                        model=model,
                        contents=prompt
                    )
                )

                generated_text = getattr(
                    response,
                    "text",
                    None
                )

                if generated_text:

                    print(
                        f"GEMINI SUCCESS: {model}"
                    )

                    return generated_text, model

                raise Exception(
                    "Gemini returned an empty response."
                )

            except Exception as error:

                last_error = error

                print(
                    f"GEMINI ERROR: "
                    f"model={model}, "
                    f"attempt={attempt + 1}, "
                    f"error={str(error)}"
                )

                if attempt == 0:
                    time.sleep(2)

        print(
            f"GEMINI FALLBACK: "
            f"moving away from {model}"
        )

    raise Exception(
        "All Gemini models failed. "
        f"Last error: {str(last_error)}"
    )


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

    if gemini_client is None:

        return {
            "success": False,
            "error": "GEMINI_API_KEY is not configured."
        }

    # -----------------------------------------------------
    # QUESTION COUNT
    # -----------------------------------------------------

    try:

        question_count = int(
            question_count
        )

    except Exception:

        question_count = 20

    question_count = max(
        10,
        min(
            question_count,
            40
        )
    )

    # -----------------------------------------------------
    # DIFFICULTY
    # -----------------------------------------------------

    allowed_difficulties = {
        "easy",
        "medium",
        "hard"
    }

    if difficulty not in allowed_difficulties:
        difficulty = "medium"

    # -----------------------------------------------------
    # QUESTION TYPE
    # -----------------------------------------------------

    allowed_question_types = {
        "multiple_choice",
        "true_false",
        "short_answer"
    }

    if question_type not in allowed_question_types:
        question_type = "multiple_choice"

    # -----------------------------------------------------
    # READ PDF
    # -----------------------------------------------------

    try:

        pdf_data = await pdf.read()

        document = fitz.open(
            stream=pdf_data,
            filetype="pdf"
        )

        full_text = ""

        for page in document:

            full_text += (
                page.get_text() +
                "\n"
            )

        page_count = len(
            document
        )

        document.close()

    except Exception as error:

        print(
            "PDF ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": (
                f"Could not read PDF: "
                f"{str(error)}"
            )
        }

    # -----------------------------------------------------
    # CHECK TEXT
    # -----------------------------------------------------

    if not full_text.strip():

        return {
            "success": False,
            "error": (
                "The PDF does not contain "
                "readable text."
            )
        }

    # -----------------------------------------------------
    # LIMIT TEXT
    # -----------------------------------------------------

    text_for_ai = full_text[:50000]

    # -----------------------------------------------------
    # QUESTION FORMAT
    # -----------------------------------------------------

    if question_type == "true_false":

        format_instruction = """
Create True/False questions.

For each question use EXACTLY this format:

Question 1: ...
Answer: True

Question 2: ...
Answer: False

Do not add A, B, C, or D options.
"""

    elif question_type == "short_answer":

        format_instruction = """
Create short-answer questions.

For each question use EXACTLY this format:

Question 1: ...
Answer: ...

Question 2: ...
Answer: ...

Do not add A, B, C, or D options.
"""

    else:

        format_instruction = """
Create multiple-choice questions.

Each question must have exactly 4 options.

For each question use EXACTLY this format:

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
"""

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are an expert educational test generator.

Read the textbook content below and create exactly
{question_count} questions.

Difficulty level:
{difficulty}

Question type:
{question_type}

IMPORTANT RULES:

1. Questions must be based ONLY on the textbook content.
2. Do not invent facts that are not supported by the textbook.
3. Do not repeat questions.
4. Keep the questions clear and suitable for students.
5. Use English only.
6. Number every question from 1 to {question_count}.
7. Do not include an introduction.
8. Do not include a conclusion.
9. Do not use Markdown code blocks.
10. Follow the requested format exactly.

{format_instruction}

TEXTBOOK CONTENT:

{text_for_ai}
"""

    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    try:

        generated_text, used_model = (
            generate_with_gemini(
                prompt
            )
        )

        if not generated_text:

            return {
                "success": False,
                "error": (
                    "Gemini returned "
                    "an empty response."
                )
            }

    except Exception as error:

        print(
            "GEMINI FINAL ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": (
                "AI generation failed: "
                f"{str(error)}"
            )
        }

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return {
        "success": True,
        "filename": pdf.filename,
        "pages": page_count,
        "text_length": len(full_text),
        "question_count": question_count,
        "difficulty": difficulty,
        "question_type": question_type,
        "model": used_model,
        "test": generated_text
    }


# =========================================================
# SAVE EXAM
# =========================================================

@app.post("/save-exam")
async def save_exam(
    title: str = Form(...),
    subject_id: int = Form(...),
    grade: str = Form(...),
    topic: str = Form(""),
    exam_type: str = Form("Practice"),
    year: str = Form(""),
    description: str = Form(""),
    file_url: str = Form(""),
    answer_url: str = Form(""),
    is_public: bool = Form(False)
):

    if supabase is None:

        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    try:

        exam_data = {
            "title": title,
            "subject_id": subject_id,
            "grade": grade,
            "topic": topic,
            "exam_type": exam_type,
            "year": year,
            "description": description,
            "file_url": file_url,
            "answer_url": answer_url,
            "is_public": is_public
        }

        response = (
            supabase
            .table("exams")
            .insert(exam_data)
            .execute()
        )

        saved_exams = (
            response.data or []
        )

        if not saved_exams:

            raise Exception(
                "Supabase created no exam record."
            )

        saved_exam = saved_exams[0]

        exam_id = saved_exam.get("id")

        if exam_id is None:

            raise Exception(
                "Supabase created the exam "
                "but returned no ID."
            )

        print(
            f"EXAM SAVED SUCCESSFULLY: "
            f"id={exam_id}"
        )

        return {
            "success": True,
            "id": exam_id,
            "exam_id": exam_id,
            "exam": saved_exam
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
# SAVE QUESTIONS
# =========================================================

@app.post("/questions")
async def save_questions(
    exam_id: int = Form(...),
    questions: str = Form(...)
):

    if supabase is None:

        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    try:

        question_list = json.loads(
            questions
        )

        if not isinstance(
            question_list,
            list
        ):

            return {
                "success": False,
                "error": (
                    "Questions must be "
                    "a JSON array."
                )
            }

        rows = []

        for item in question_list:

            if not isinstance(
                item,
                dict
            ):
                continue

            rows.append({
                "exam_id": exam_id,
                "question": item.get(
                    "question",
                    ""
                ),
                "options": item.get(
                    "options",
                    []
                ),
                "answer": item.get(
                    "answer",
                    ""
                ),
                "difficulty": item.get(
                    "difficulty",
                    "medium"
                ),
                "question_type": item.get(
                    "question_type",
                    "multiple_choice"
                )
            })

        if not rows:

            return {
                "success": False,
                "error": (
                    "No questions were provided."
                )
            }

        response = (
            supabase
            .table("questions")
            .insert(rows)
            .execute()
        )

        print(
            f"QUESTIONS SAVED: "
            f"exam_id={exam_id}, "
            f"count={len(rows)}"
        )

        return {
            "success": True,
            "exam_id": exam_id,
            "count": len(rows),
            "questions": response.data or []
        }

    except json.JSONDecodeError:

        return {
            "success": False,
            "error": "Invalid questions JSON."
        }

    except Exception as error:

        print(
            "SAVE QUESTIONS ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


# =========================================================
# GET EXAMS
# =========================================================

@app.get("/exams")
def get_exams():

    if supabase is None:

        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    try:

        exams_response = (
            supabase
            .table("exams")
            .select(
                "id, title, subject_id, grade, topic, "
                "exam_type, year, description, file_url, "
                "answer_url, is_public, created_at"
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        subjects_response = (
            supabase
            .table("subjects")
            .select(
                "id, Name"
            )
            .execute()
        )

        subject_map = {}

        for subject_row in (
            subjects_response.data or []
        ):

            subject_map[
                subject_row["id"]
            ] = subject_row["Name"]

        exams = []

        for exam in (
            exams_response.data or []
        ):

            exam["subject_name"] = (
                subject_map.get(
                    exam.get(
                        "subject_id"
                    ),
                    "Unknown"
                )
            )

            exams.append(
                exam
            )

        return {
            "success": True,
            "exams": exams
        }

    except Exception as error:

        print(
            "GET EXAMS ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


# =========================================================
# GET ONE EXAM
# =========================================================

@app.get("/exams/{exam_id}")
def get_exam(
    exam_id: int
):

    if supabase is None:

        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    try:

        exam_response = (
            supabase
            .table("exams")
            .select("*")
            .eq(
                "id",
                exam_id
            )
            .single()
            .execute()
        )

        questions_response = (
            supabase
            .table("questions")
            .select("*")
            .eq(
                "exam_id",
                exam_id
            )
            .order(
                "id"
            )
            .execute()
        )

        exam = exam_response.data

        if exam:

            subject_response = (
                supabase
                .table("subjects")
                .select(
                    "id, Name"
                )
                .eq(
                    "id",
                    exam.get(
                        "subject_id"
                    )
                )
                .single()
                .execute()
            )

            if subject_response.data:

                exam["subject_name"] = (
                    subject_response
                    .data
                    .get("Name")
                )

        return {
            "success": True,
            "exam": exam,
            "questions": (
                questions_response.data
                or []
            )
        }

    except Exception as error:

        print(
            "GET EXAM ERROR:",
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }
