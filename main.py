import os
import json
import time
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import fitz

from google import genai
from supabase import create_client, Client


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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is not set in environment variables"
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_KEY is not set in environment variables"
    )

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in environment variables"
    )


SUPABASE_URL = SUPABASE_URL.strip().strip('"').strip("'")
SUPABASE_KEY = SUPABASE_KEY.strip().strip('"').strip("'")
GEMINI_API_KEY = GEMINI_API_KEY.strip().strip('"').strip("'")


if not SUPABASE_URL.startswith("https://"):
    raise RuntimeError(
        "SUPABASE_URL must start with https://"
    )


# =========================================================
# CLIENTS
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

client = genai.Client(
    api_key=GEMINI_API_KEY
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
# TEST SUPABASE
# =========================================================

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


# =========================================================
# DEBUG ROLE
# =========================================================

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

    # -----------------------------------------------------
    # QUESTION COUNT
    # -----------------------------------------------------

    question_count = max(
        10,
        min(question_count, 40)
    )


    # -----------------------------------------------------
    # DIFFICULTY
    # -----------------------------------------------------

    if difficulty not in [
        "easy",
        "medium",
        "hard"
    ]:

        difficulty = "medium"


    # -----------------------------------------------------
    # QUESTION TYPE
    # -----------------------------------------------------

    if question_type not in [
        "multiple_choice",
        "true_false",
        "short_answer"
    ]:

        question_type = "multiple_choice"


    # =====================================================
    # READ PDF
    # =====================================================

    try:

        pdf_data = await pdf.read()

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


    # =====================================================
    # CHECK PDF TEXT
    # =====================================================

    if not text.strip():

        return {
            "success": False,
            "message": "Could not extract text from this PDF."
        }


    # =====================================================
    # QUESTION FORMAT
    # =====================================================

    if question_type == "multiple_choice":

        format_instruction = """
Each question must have exactly this structure:

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
Each question must have exactly this structure:

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
Each question must have exactly this structure:

{
  "question": "Question text",
  "options": {},
  "answer": "Short correct answer"
}
"""


    # =====================================================
    # DIFFICULTY INSTRUCTION
    # =====================================================

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


    # =====================================================
    # GEMINI PROMPT
    # =====================================================

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
8. Difficulty level: {difficulty}.
9. {difficulty_instruction}
10. Question type: {question_type}.

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


    # =====================================================
    # CALL GEMINI WITH RETRY
    # =====================================================

    try:

        response = None
        last_error = None

        # Try up to 3 times
        for attempt in range(3):

            try:

                print(
                    f"Gemini attempt {attempt + 1}/3"
                )

                response = client.models.generate_content(

                    model="gemini-3.6-flash",

                    contents=prompt

                )


                # Check response

                if response and response.text:

                    print(
                        f"Gemini attempt {attempt + 1} succeeded"
                    )

                    break


                last_error = Exception(
                    "Gemini returned an empty response."
                )


            except Exception as e:

                last_error = e

                print(
                    f"Gemini attempt {attempt + 1} failed: "
                    f"{repr(e)}"
                )


                # Wait before trying again

                if attempt < 2:

                    wait_time = 5 * (attempt + 1)

                    print(
                        f"Waiting {wait_time} seconds before retry..."
                    )

                    time.sleep(wait_time)


        # -------------------------------------------------
        # NO SUCCESS
        # -------------------------------------------------

        if response is None or not response.text:

            raise Exception(
                "Gemini is temporarily unavailable. "
                "Please try again in a few minutes. "
                f"Last error: {last_error}"
            )


        ai_text = response.text.strip()


    except Exception as e:

        return {

            "success": False,

            "message":
                f"AI generation failed: {str(e)}"

        }


    # =====================================================
    # CLEAN GEMINI RESPONSE
    # =====================================================

    if ai_text.startswith("```json"):

        ai_text = ai_text[7:]


    elif ai_text.startswith("```"):

        ai_text = ai_text[3:]


    if ai_text.endswith("```"):

        ai_text = ai_text[:-3]


    ai_text = ai_text.strip()


    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        data = json.loads(ai_text)

        questions = data.get(
            "questions",
            []
        )


        if not isinstance(
            questions,
            list
        ):

            return {

                "success": False,

                "message":
                    "AI returned an invalid questions format.",

                "raw_response":
                    ai_text

            }


        if not questions:

            return {

                "success": False,

                "message":
                    "AI returned no questions.",

                "raw_response":
                    ai_text

            }


    except Exception as e:

        return {

            "success": False,

            "message":
                "AI returned an invalid question format.",

            "raw_response":
                ai_text,

            "error":
                str(e)

        }


    # =====================================================
    # LIMIT QUESTION COUNT
    # =====================================================

    questions = questions[:question_count]


    # =====================================================
    # CLEAN QUESTIONS
    # =====================================================

    cleaned_questions = []


    for q in questions:

        if not isinstance(
            q,
            dict
        ):

            continue


        question_text = str(
            q.get(
                "question",
                ""
            )
        ).strip()


        answer = str(
            q.get(
                "answer",
                ""
            )
        ).strip()


        options = q.get(
            "options",
            {}
        )


        if not isinstance(
            options,
            dict
        ):

            options = {}


        if not question_text:

            continue


        cleaned_questions.append({

            "question":
                question_text,

            "options":
                options,

            "answer":
                answer,

            "difficulty":
                difficulty,

            "question_type":
                question_type

        })


    # =====================================================
    # CHECK VALID QUESTIONS
    # =====================================================

    if not cleaned_questions:

        return {

            "success": False,

            "message":
                "No valid questions were generated."

        }


    # =====================================================
    # RETURN QUESTIONS
    # =====================================================

    return {

        "success": True,

        "filename":
            pdf.filename,

        "pages":
            pages,

        "num_questions":
            len(cleaned_questions),

        "difficulty":
            difficulty,

        "question_type":
            question_type,

        "language":
            "english",

        "questions":
            cleaned_questions

    }


# =========================================================
# SAVE EXAM REQUEST
# =========================================================

class SaveExamRequest(BaseModel):

    title: str

    subject_id: int

    grade: str = ""

    topic: str = ""

    exam_type: str = ""

    year: Optional[int] = None

    description: str = ""

    file_url: str = ""

    answer_url: str = ""

    difficulty: str = "medium"

    question_type: str = "multiple_choice"

    questions: List[Dict[str, Any]]


# =========================================================
# SAVE EXAM
# =========================================================

@app.post("/save-exam")
def save_exam(
    data: SaveExamRequest
):

    # -----------------------------------------------------
    # CHECK TITLE
    # -----------------------------------------------------

    if not data.title.strip():

        return {

            "success": False,

            "message":
                "Exam title is required."

        }


    # -----------------------------------------------------
    # CHECK SUBJECT
    # -----------------------------------------------------

    if data.subject_id not in range(1, 9):

        return {

            "success": False,

            "message":
                "Invalid subject_id. Use 1 to 8."

        }


    # -----------------------------------------------------
    # CHECK QUESTIONS
    # -----------------------------------------------------

    if not data.questions:

        return {

            "success": False,

            "message":
                "There are no questions to save."

        }


    # -----------------------------------------------------
    # DIFFICULTY
    # -----------------------------------------------------

    if data.difficulty not in [
        "easy",
        "medium",
        "hard"
    ]:

        data.difficulty = "medium"


    # -----------------------------------------------------
    # QUESTION TYPE
    # -----------------------------------------------------

    if data.question_type not in [
        "multiple_choice",
        "true_false",
        "short_answer"
    ]:

        data.question_type = "multiple_choice"


    # =====================================================
    # CREATE EXAM ROW
    # =====================================================

    exam_row = {

        "title":
            data.title.strip(),

        "subject_id":
            data.subject_id,

        "grade":
            data.grade.strip(),

        "topic":
            data.topic.strip(),

        "exam_type":
            data.exam_type.strip(),

        "year":
            data.year,

        "description":
            data.description.strip(),

        "file_url":
            data.file_url.strip(),

        "answer_url":
            data.answer_url.strip()

    }


    # =====================================================
    # INSERT EXAM
    # =====================================================

    try:

        exam_result = (

            supabase
            .table("exams")
            .insert(exam_row)
            .select("id")
            .single()
            .execute()

        )


        if not exam_result.data:

            return {

                "success": False,

                "message":
                    "Supabase did not return the new exam ID."

            }


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


    # =====================================================
    # PREPARE QUESTION ROWS
    # =====================================================

    question_rows = []


    for q in data.questions:

        if not isinstance(
            q,
            dict
        ):

            continue


        question_text = q.get(
            "question",
            ""
        )


        answer = q.get(
            "answer",
            ""
        )


        options = q.get(
            "options",
            {}
        )


        if question_text is None:

            question_text = ""


        if answer is None:

            answer = ""


        if not isinstance(
            options,
            dict
        ):

            options = {}


        question_text = str(
            question_text
        ).strip()


        answer = str(
            answer
        ).strip()


        if not question_text:

            continue


        question_rows.append({

            "exam_id":
                exam_id,

            "question":
                question_text,

            "options":
                options,

            "answer":
                answer,

            "difficulty":
                data.difficulty,

            "question_type":
                data.question_type

        })


    # =====================================================
    # CHECK QUESTION ROWS
    # =====================================================

    if not question_rows:

        return {

            "success": False,

            "message":
                "There are no valid questions to save.",

            "exam_id":
                exam_id

        }


    # =====================================================
    # INSERT QUESTIONS
    # =====================================================

    try:

        question_result = (

            supabase
            .table("questions")
            .insert(question_rows)
            .execute()

        )


        saved_count = (

            len(question_result.data)

            if question_result.data

            else 0

        )


        print(
            "SAVED QUESTIONS:",
            saved_count
        )


    except Exception as e:

        print(
            "QUESTION INSERT ERROR:",
            repr(e)
        )


        return {

            "success": False,

            "message":
                "Exam was created, but questions "
                "could not be saved: " + str(e),

            "exam_id":
                exam_id

        }


    # =====================================================
    # SUCCESS
    # =====================================================

    return {

        "success": True,

        "message":
            "Exam and questions saved successfully.",

        "exam_id":
            exam_id,

        "num_questions":
            len(question_rows)

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

            "questions":
                result.data

        }


    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)

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
            .order(
                "created_at",
                desc=True
            )
            .execute()

        )


        return {

            "success": True,

            "exams":
                result.data

        }


    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)

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

            "data":
                result.data

        }


    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)

        }
