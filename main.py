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


app = FastAPI(
    title="Text2Test AI",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is not set")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")


SUPABASE_URL = SUPABASE_URL.strip().strip('"').strip("'")
SUPABASE_KEY = SUPABASE_KEY.strip().strip('"').strip("'")
GEMINI_API_KEY = GEMINI_API_KEY.strip().strip('"').strip("'")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Text2Test AI backend is running!"
    }


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
            "message": str(e)
        }


@app.get("/subjects")
def get_subjects():
    try:
        result = (
            supabase
            .table("subjects")
            .select("*")
            .order("id")
            .execute()
        )

        return {
            "success": True,
            "subjects": result.data
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(...),
    question_count: int = Form(20),
    difficulty: str = Form("medium"),
    question_type: str = Form("multiple_choice")
):

    question_count = max(10, min(question_count, 40))

    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"

    if question_type not in [
        "multiple_choice",
        "true_false",
        "short_answer"
    ]:
        question_type = "multiple_choice"


    try:
        pdf_data = await pdf.read()

        document = fitz.open(
            stream=pdf_data,
            filetype="pdf"
        )

        text_parts = []

        for page in document:
            page_text = page.get_text()

            if page_text:
                text_parts.append(page_text)

        pages = len(document)

        document.close()

        text = "\n".join(text_parts)

    except Exception as e:
        return {
            "success": False,
            "message": f"Could not read PDF: {str(e)}"
        }


    if not text.strip():
        return {
            "success": False,
            "message": "Could not extract text from this PDF."
        }


    if question_type == "multiple_choice":

        format_instruction = """
Each question must contain:

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
Each question must contain:

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
Each question must contain:

{
  "question": "Question text",
  "options": {},
  "answer": "Short correct answer"
}
"""


    difficulty_instruction = {
        "easy": "Test basic knowledge and understanding.",
        "medium": "Test understanding and application.",
        "hard": "Test deeper reasoning and application."
    }[difficulty]


    textbook_text = text[:30000]


    prompt = f"""
You are an expert educational test creator.

Create exactly {question_count} questions
using ONLY the textbook content below.

Rules:

1. All questions must be in English.
2. All answer choices must be in English.
3. All answers must be in English.
4. Do not use outside knowledge.
5. Do not invent facts.
6. Do not repeat questions.
7. Focus on important concepts.
8. Difficulty: {difficulty}.
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

There must be exactly {question_count} questions.

Do not use Markdown.
Do not use code fences.
Do not add explanations.

TEXTBOOK CONTENT:

{textbook_text}
"""


    response = None
    last_error = None


    for attempt in range(3):

        try:

            print(
                f"Gemini attempt {attempt + 1}/3"
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            if response and response.text:

                print(
                    f"Gemini attempt {attempt + 1} succeeded"
                )

                break

            last_error = "Empty Gemini response"

        except Exception as e:

            last_error = str(e)

            print(
                f"Gemini attempt {attempt + 1} failed: {e}"
            )

            if attempt < 2:
                time.sleep(5)


    if response is None or not response.text:

        return {
            "success": False,
            "message": (
                "AI generation failed. "
                f"Last error: {last_error}"
            )
        }


    ai_text = response.text.strip()


    if ai_text.startswith("```json"):
        ai_text = ai_text[7:]

    elif ai_text.startswith("```"):
        ai_text = ai_text[3:]


    if ai_text.endswith("```"):
        ai_text = ai_text[:-3]


    ai_text = ai_text.strip()


    try:

        data = json.loads(ai_text)

        questions = data.get(
            "questions",
            []
        )

        if not isinstance(questions, list):

            return {
                "success": False,
                "message": "Invalid questions format.",
                "raw_response": ai_text
            }

    except Exception as e:

        return {
            "success": False,
            "message": "Could not parse AI response.",
            "raw_response": ai_text,
            "error": str(e)
        }


    questions = questions[:question_count]

    cleaned_questions = []


    for q in questions:

        if not isinstance(q, dict):
            continue


        question_text = str(
            q.get("question", "")
        ).strip()


        answer = str(
            q.get("answer", "")
        ).strip()


        options = q.get(
            "options",
            {}
        )


        if not isinstance(options, dict):
            options = {}


        if not question_text:
            continue


        cleaned_questions.append({
            "question": question_text,
            "options": options,
            "answer": answer,
            "difficulty": difficulty,
            "question_type": question_type
        })


    if not cleaned_questions:

        return {
            "success": False,
            "message": "No valid questions were generated."
        }


    return {
        "success": True,
        "filename": pdf.filename,
        "pages": pages,
        "num_questions": len(cleaned_questions),
        "difficulty": difficulty,
        "question_type": question_type,
        "language": "english",
        "questions": cleaned_questions
    }


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


@app.post("/save-exam")
def save_exam(data: SaveExamRequest):

    if not data.title.strip():

        return {
            "success": False,
            "message": "Exam title is required."
        }


    if data.subject_id < 1:

        return {
            "success": False,
            "message": "Invalid subject ID."
        }


    if not data.questions:

        return {
            "success": False,
            "message": "There are no questions to save."
        }


    if data.difficulty not in [
        "easy",
        "medium",
        "hard"
    ]:

        data.difficulty = "medium"


    if data.question_type not in [
        "multiple_choice",
        "true_false",
        "short_answer"
    ]:

        data.question_type = "multiple_choice"


    try:

        subject_result = (
            supabase
            .table("subjects")
            .select("id")
            .eq(
                "id",
                data.subject_id
            )
            .limit(1)
            .execute()
        )


        if not subject_result.data:

            return {
                "success": False,
                "message": "Subject does not exist."
            }


    except Exception as e:

        return {
            "success": False,
            "message": (
                "Could not verify subject: "
                f"{str(e)}"
            )
        }


    exam_row = {

        "title": data.title.strip(),

        "subject_id": data.subject_id,

        "grade": data.grade.strip(),

        "topic": data.topic.strip(),

        "exam_type": data.exam_type.strip(),

        "year": data.year,

        "description": data.description.strip(),

        "file_url": data.file_url.strip(),

        "answer_url": data.answer_url.strip()
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


        if not exam_result.data:

            return {
                "success": False,
                "message": "Could not create exam."
            }


        exam_id = exam_result.data["id"]


    except Exception as e:

        print(
            f"Exam insert error: {e}"
        )

        return {
            "success": False,
            "message": (
                "Could not save exam to Supabase: "
                f"{str(e)}"
            )
        }


    question_rows = []


    for q in data.questions:

        if not isinstance(q, dict):
            continue


        question_text = str(
            q.get("question", "")
        ).strip()


        answer = str(
            q.get("answer", "")
        ).strip()


        options = q.get(
            "options",
            {}
        )


        if not isinstance(options, dict):
            options = {}


        if not question_text:
            continue


        question_rows.append({

            "exam_id": exam_id,

            "question": question_text,

            "options": options,

            "answer": answer,

            "difficulty": data.difficulty,

            "question_type": data.question_type
        })


    if not question_rows:

        return {
            "success": False,
            "message": "No valid questions to save.",
            "exam_id": exam_id
        }


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


        return {

            "success": True,

            "message": (
                "Exam and questions "
                "saved successfully."
            ),

            "exam_id": exam_id,

            "num_questions": saved_count
        }


    except Exception as e:

        print(
            f"Question insert error: {e}"
        )


        return {

            "success": False,

            "message": (
                "Exam was created, but "
                "questions could not be saved: "
                f"{str(e)}"
            ),

            "exam_id": exam_id
        }


@app.get("/questions")
def get_questions(
    exam_id: Optional[int] = None
):

    try:

        query = (
            supabase
            .table("questions")
            .select("*")
        )


        if exam_id is not None:

            query = query.eq(
                "exam_id",
                exam_id
            )


        result = query.execute()


        return {
            "success": True,
            "questions": result.data
        }


    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


@app.get("/exams")
def get_exams(
    subject_id: Optional[int] = None,
    grade: Optional[str] = None,
    search: Optional[str] = None
):

    try:

        query = (
            supabase
            .table("exams")
            .select("*, subjects(id, Name)")
            .order(
                "created_at",
                desc=True
            )
        )


        if subject_id is not None:

            query = query.eq(
                "subject_id",
                subject_id
            )


        if grade:

            query = query.eq(
                "grade",
                grade
            )


        if search:

            search = search.strip()

            if search:

                query = query.or_(
                    "title.ilike.%"
                    + search
                    + ",topic.ilike.%"
                    + search
                    + ",description.ilike.%"
                    + search
                )


        result = query.execute()


        return {

            "success": True,

            "exams": result.data,

            "count": len(result.data)
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


@app.get("/exams/{exam_id}")
def get_exam(exam_id: int):

    try:

        exam_result = (
            supabase
            .table("exams")
            .select("*, subjects(id, Name)")
            .eq(
                "id",
                exam_id
            )
            .single()
            .execute()
        )


        if not exam_result.data:

            return {
                "success": False,
                "message": "Exam not found."
            }


        question_result = (
            supabase
            .table("questions")
            .select("*")
            .eq(
                "exam_id",
                exam_id
            )
            .order(
                "id",
                desc=False
            )
            .execute()
        )


        return {

            "success": True,

            "exam": exam_result.data,

            "questions": question_result.data,

            "num_questions": len(
                question_result.data
            )
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }
