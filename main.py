import os
import json

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import fitz

from google import genai
from supabase import create_client, Client


# =========================
# APP
# =========================

app = FastAPI()


# =========================
# SUPABASE
# =========================

from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set in environment variables")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is not set in environment variables")

# Remove accidental spaces or quotes
SUPABASE_URL = SUPABASE_URL.strip().strip('"').strip("'")
SUPABASE_KEY = SUPABASE_KEY.strip().strip('"').strip("'")

# Make sure the URL points to the Supabase project
if not SUPABASE_URL.startswith("https://"):
    raise RuntimeError(
        "SUPABASE_URL must start with https://"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


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


# =========================
# UPLOAD PDF + GENERATE TEST
# =========================

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

    if difficulty not in ["easy", "medium", "hard"]:
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
    # QUESTION TYPE
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
        "easy": "Test basic facts and understanding.",
        "medium": "Test understanding and application.",
        "hard": "Require deeper reasoning, comparison, analysis, or application."
    }.get(
        difficulty,
        "Test understanding and application."
    )


    # =========================
    # PROMPT
    # =========================

    prompt = f"""
You are an expert educational test creator.

Create EXACTLY {question_count} questions from the textbook content below.

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

There must be EXACTLY {question_count} objects inside the "questions" array.

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
    # LIMIT QUESTIONS AGAIN
    # =========================

    questions = questions[:question_count]


    # =========================
    # SAVE QUESTIONS TO SUPABASE
    # =========================

    try:
        rows = []

        for q in questions:

            options = q.get("options", {})

            if not isinstance(options, dict):
                options = {}

            answer = q.get(
                "answer",
                ""
            )

            if answer is None:
                answer = ""

            question_text = q.get(
                "question",
                ""
            )

            if question_text is None:
                question_text = ""

            rows.append({
                "question": str(question_text),
                "options": options,
                "answer": str(answer),
                "difficulty": difficulty,
                "question_type": question_type
            })


        if not rows:
            return {
                "success": False,
                "message": "There are no questions to save."
            }


        # INSERT INTO SUPABASE
        result = (
            supabase
            .table("questions")
            .insert(rows)
            .execute()
        )


        print(
            "SUPABASE INSERT RESULT:",
            result
        )


        # Check response
        if hasattr(result, "data"):
            print(
                "SUPABASE SAVED ROWS:",
                len(result.data)
            )


    except Exception as e:

        print(
            "SUPABASE INSERT ERROR:",
            repr(e)
        )

        return {
            "success": False,
            "message": (
                "Could not save questions "
                f"to Supabase: {str(e)}"
            )
        }


    # =========================
    # RETURN
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
@app.get("/check-supabase")
def check_supabase():
    try:
        result = supabase.table("questions").select("*").limit(1).execute()
        return {
            "success": True,
            "data": result.data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
@app.get("/questions")
def get_questions():
    try:
        result = supabase.table("questions").select("*").execute()

        return {
            "success": True,
            "questions": result.data
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
