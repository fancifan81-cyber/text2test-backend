import os
import json

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import fitz

from google import genai
from supabase import create_client, Client


# =========================
# APP
# =========================

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
# SUPABASE
# =========================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is not set in environment variables"
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_KEY is not set in environment variables"
    )

SUPABASE_URL = SUPABASE_URL.strip().strip('"').strip("'")
SUPABASE_KEY = SUPABASE_KEY.strip().strip('"').strip("'")

if not SUPABASE_URL.startswith("https://"):
    raise RuntimeError(
        "SUPABASE_URL must start with https://"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================
# GEMINI
# =========================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in environment variables"
    )

GEMINI_API_KEY = GEMINI_API_KEY.strip().strip('"').strip("'")

client = genai.Client(
    api_key=GEMINI_API_KEY
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
# TEST SUPABASE
# =========================

@app.get("/test-supabase")
def test_supabase():

    try:

        result = (
            supabase
            .table("questions")
            .select("*")
            .limit(1)
            .execute()
        )

        return {
            "success": True,
            "message": "Supabase connection is working!",
            "data": result.data
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Supabase connection failed: {str(e)}"
        }


# =========================
# DEBUG SUPABASE ROLE
# =========================

@app.get("/debug-role")
def debug_role():

    try:

        result = (
            supabase
            .rpc("get_request_role")
            .execute()
        )

        return {
            "success": True,
            "role": result.data
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================================================
# UPLOAD PDF + GENERATE QUESTIONS
# =========================================================

@app.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(...),
    question_count: int = Form(20),
    difficulty: str = Form("medium"),
    question_type: str = Form("multiple_choice"),
):

    # =========================
    # LIMIT QUESTIONS
    # =========================

    question_count = max(
        10,
        min(question_count, 40)
    )


    # =========================
    # VALIDATE DIFFICULTY
    # =========================

    if difficulty not in [
        "easy",
        "medium",
        "hard"
    ]:
        difficulty = "medium"


    # =========================
    # VALIDATE QUESTION TYPE
    # =========================

    if question_type not in [
        "multiple_choice",
        "true_false",
        "short_answer"
    ]:
        question_type = "multiple_choice"


    # =========================
    # READ PDF
    # =========================

    pdf_data = await pdf.read()

    try:

        document = fitz.open(
            stream=pdf_data,
            filetype="pdf"
        )

        text = ""

        for page in document:
            text += page.get_text()
            text += "\n"

        pages = len(document)

        document.close()

    except Exception as e:

        return {
            "success": False,
            "message": f"Could not read PDF: {str(e)}"
        }


    # =========================
    # CHECK TEXT
    # =========================

    if not text.strip():

        return {
            "success": False,
            "message": "Could not extract text from this PDF."
        }


    # =========================
    # QUESTION FORMAT
    # =========================

    if question_type == "multiple_choice":

        format_instruction = """
Each question must have:

{
  "question": "Question text",
  "options": {
    "A": "Option A",
    "B": "Option B",
    "C": "Option C",
    "D": "Option D"
  },
  "answer": "A"
}
"""

    elif question_type == "true_false":

        format_instruction = """
Each question must have:

{
  "question": "Question text",
  "options": {
    "A": "True",
    "B": "False"
  },
  "answer": "A"
}
"""

    else:

        format_instruction = """
Each question must have:

{
  "question": "Question text",
  "options": {},
  "answer": "Short correct answer"
}
"""


    # =========================
    # DIFFICULTY
    # =========================

    difficulty_instruction = {

        "easy":
            "Test basic facts and understanding.",

        "medium":
            "Test understanding and application.",

        "hard":
            "Require deeper reasoning, comparison, analysis, or application."

    }.get(
        difficulty,
        "Test understanding and application."
    )


    # =========================
    # GEMINI PROMPT
    # =========================

    prompt = f"""
You are an expert educational test creator.

Create EXACTLY {question_count} questions
from the textbook content below.

IMPORTANT RULES:

1. Use ONLY information contained in the textbook.
2. Do NOT use outside knowledge.
3. Do NOT invent facts.
4. Focus on important concepts.
5. Avoid extremely minor details.
6. All questions must be in ENGLISH.
7. All answers must be in ENGLISH.
8. Difficulty: {difficulty}.
9. {difficulty_instruction}

Question type: {question_type}

{format_instruction}

Return ONLY valid JSON.

The JSON must have exactly this structure:

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
      "answer": "A"
    }}
  ]
}}

There must be EXACTLY {question_count}
objects inside the "questions" array.

Do not write Markdown.

Do not write ```json.

Do not add any explanation.

TEXTBOOK CONTENT:

{text[:30000]}
"""


    # =========================
    # CALL GEMINI
    # =========================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        ai_text = response.text.strip()

    except Exception as e:

        return {
            "success": False,
            "message": f"AI generation failed: {str(e)}"
        }


    # =========================
    # CLEAN AI RESPONSE
    # =========================

    if ai_text.startswith("```json"):

        ai_text = ai_text[7:]

    elif ai_text.startswith("```"):

        ai_text = ai_text[3:]

    if ai_text.endswith("```"):

        ai_text = ai_text[:-3]

    ai_text = ai_text.strip()


    # =========================
    # PARSE JSON
    # =========================

    try:

        data = json.loads(ai_text)

        questions = data.get(
            "questions",
            []
        )

        if not questions:

            return {
                "success": False,
                "message": "AI returned no questions.",
                "raw_response": ai_text
            }

    except Exception as e:

        return {
            "success": False,
            "message": "AI returned an invalid question format.",
            "raw_response": ai_text,
            "error": str(e)
        }


    # =========================
    # LIMIT AGAIN
    # =========================

    questions = questions[:question_count]


    # =========================
    # RETURN QUESTIONS
    # =========================
    #
    # IMPORTANT:
    # We DO NOT save questions here.
    #
    # The user will first choose:
    # - title
    # - subject
    # - grade
    # - topic
    # - exam type
    #
    # Then /save-exam will save everything.
    # =========================

    return {

        "success": True,

        "filename": pdf.filename,

        "pages": pages,

        "num_questions": len(questions),

        "difficulty": difficulty,

        "question_type": question_type,

        "language": "english",

        "questions": questions
    }


# =========================================================
# SAVE EXAM
# =========================================================

class SaveExamRequest(BaseModel):

    title: str

    subject_id: int

    grade: str = ""

    topic: str = ""

    exam_type: str = ""

    year: int | None = None

    description: str = ""

    file_url: str = ""

    answer_url: str = ""

    difficulty: str = "medium"

    question_type: str = "multiple_choice"

    questions: list


@app.post("/save-exam")
def save_exam(data: SaveExamRequest):

    # =========================
    # VALIDATE
    # =========================

    if not data.title.strip():

        return {
            "success": False,
            "message": "Exam title is required."
        }


    if data.subject_id not in range(1, 9):

        return {
            "success": False,
            "message": "Invalid subject_id. Use 1 to 8."
        }


    if not data.questions:

        return {
            "success": False,
            "message": "There are no questions to save."
        }


    # =========================
    # CREATE EXAM
    # =========================

    exam_row = {

        "title": data.title.strip(),

        "subject_id": data.subject_id,

        "grade": data.grade,

        "topic": data.topic,

        "exam_type": data.exam_type,

        "year": data.year,

        "description": data.description,

        "file_url": data.file_url,

        "answer_url": data.answer_url
    }


    try:

        exam_result = (
            supabase
            .table("exams")
            .insert(exam_row)
            .select("id")
            .single()
            .execute()
        )

        exam_id = exam_result.data["id"]

        print(
            "CREATED EXAM:",
            exam_id
        )

    except Exception as e:

        print(
            "EXAM INSERT ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "message":
                f"Could not save exam to Supabase: {str(e)}"
        }


    # =========================
    # PREPARE QUESTIONS
    # =========================

    question_rows = []

    for q in data.questions:

        options = q.get(
            "options",
            {}
        )

        if not isinstance(options, dict):

            options = {}


        question_text = q.get(
            "question",
            ""
        )

        if question_text is None:

            question_text = ""


        answer = q.get(
            "answer",
            ""
        )

        if answer is None:

            answer = ""


        question_rows.append({

            "exam_id": exam_id,

            "question":
                str(question_text),

            "options":
                options,

            "answer":
                str(answer),

            "difficulty":
                data.difficulty,

            "question_type":
                data.question_type
        })


    if not question_rows:

        return {

            "success": False,

            "message": "There are no questions to save."
        }


    # =========================
    # SAVE QUESTIONS
    # =========================

    try:

        question_result = (
            supabase
            .table("questions")
            .insert(question_rows)
            .execute()
        )

        print(
            "SAVED QUESTIONS:",
            len(question_result.data)
            if question_result.data
            else 0
        )

    except Exception as e:

        print(
            "QUESTION INSERT ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "message":
                "Exam was created, but questions could not be saved: "
                f"{str(e)}",

            "exam_id":
                exam_id
        }


    # =========================
    # SUCCESS
    # =========================

    return {

        "success": True,

        "message": "Exam and questions saved successfully.",

        "exam_id": exam_id,

        "num_questions":
            len(question_rows)
    }


# =========================================================
# CHECK SUPABASE
# =========================================================

@app.get("/check-supabase")
def check_supabase():

    try:

        result = (
            supabase
            .table("questions")
            .select("*")
            .limit(1)
            .execute()
        )

        return {

            "success": True,

            "data": result.data
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# =========================================================
# GET QUESTIONS
# =========================================================

@app.get("/questions")
def get_questions():

    try:

        result = (
            supabase
            .table("questions")
            .select("*")
            .execute()
        )

        return {

            "success": True,

            "questions": result.data
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# =========================================================
# GET EXAMS
# =========================================================

@app.get("/exams")
def get_exams():

    try:

        result = (
            supabase
            .table("exams")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return {

            "success": True,

            "exams": result.data
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }
