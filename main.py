import os
import json
import re

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import fitz

from google import genai
from supabase import create_client, Client

# =========================================================

# CONFIGURATION

# =========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get(
"GEMINI_MODEL",
"gemini-3.6-flash"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")

SUPABASE_KEY = (
os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
or os.environ.get("SUPABASE_KEY")
)

# =========================================================

# APP

# =========================================================

app = FastAPI(
title="Text2Test AI API",
version="1.0.0"
)

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
supabase: Client | None = None

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
"gemini_model": GEMINI_MODEL
}

# =========================================================

# SUPABASE TEST

# =========================================================

@app.get("/test-supabase")
def test_supabase():
try:
if not supabase:
return {
"success": False,
"error": "Supabase is not configured."
}

```
    response = (
        supabase
        .table("subjects")
        .select("id, Name")
        .limit(10)
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
```

# =========================================================

# DEBUG ROLE

# =========================================================

@app.get("/debug-role")
def debug_role():
try:
if not supabase:
return {
"success": False,
"error": "Supabase is not configured."
}

```
    response = (
        supabase
        .table("subjects")
        .select("id")
        .limit(1)
        .execute()
    )

    return {
        "success": True,
        "role": "backend",
        "test": response.data or []
    }

except Exception as error:
    return {
        "success": False,
        "error": str(error)
    }
```

# =========================================================

# CHECK SUPABASE

# =========================================================

@app.get("/check-supabase")
def check_supabase():

```
result = {
    "success": True,
    "supabase_configured": bool(
        SUPABASE_URL and SUPABASE_KEY
    ),
    "subjects": False,
    "exams": False,
    "questions": False,
    "errors": []
}

if not supabase:
    result["success"] = False
    result["errors"].append(
        "Supabase client is not configured."
    )
    return result

# Check subjects
try:
    supabase \
        .table("subjects") \
        .select("id, Name") \
        .limit(1) \
        .execute()

    result["subjects"] = True

except Exception as error:
    result["success"] = False
    result["errors"].append(
        "subjects: " + str(error)
    )

# Check exams
try:
    supabase \
        .table("exams") \
        .select("id") \
        .limit(1) \
        .execute()

    result["exams"] = True

except Exception as error:
    result["success"] = False
    result["errors"].append(
        "exams: " + str(error)
    )

# Check questions
try:
    supabase \
        .table("questions") \
        .select("id") \
        .limit(1) \
        .execute()

    result["questions"] = True

except Exception as error:
    result["success"] = False
    result["errors"].append(
        "questions: " + str(error)
    )

return result
```

# =========================================================

# GET SUBJECTS

# =========================================================

#

# IMPORTANT:

# Your database uses:

#

# subjects.id

# subjects.Name

#

# NOT:

#

# subjects.name

#

# Therefore this endpoint explicitly uses "Name".

#

# =========================================================

@app.get("/subjects")
def get_subjects():

```
try:

    if not supabase:
        return {
            "success": False,
            "error": "Supabase is not configured."
        }

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
```

# =========================================================

# EXTRACT PDF TEXT

# =========================================================

def extract_pdf_text(pdf_data: bytes):

```
document = fitz.open(
    stream=pdf_data,
    filetype="pdf"
)

pages = len(document)

text_parts = []

for page in document:

    page_text = page.get_text()

    if page_text:
        text_parts.append(
            page_text
        )

document.close()

full_text = "\n".join(
    text_parts
).strip()

return full_text, pages
```

# =========================================================

# CLEAN GEMINI RESPONSE

# =========================================================

def clean_ai_response(text: str):

````
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

# Find first JSON object
first_brace = text.find("{")

if first_brace > 0:
    text = text[first_brace:]

# Find final JSON object
last_brace = text.rfind("}")

if last_brace >= 0:
    text = text[:last_brace + 1]

return text.strip()
````

# =========================================================

# NORMALIZE QUESTION

# =========================================================

def normalize_question(question):

```
if not isinstance(question, dict):
    return None

question_text = str(
    question.get(
        "question",
        ""
    )
).strip()

if not question_text:
    return None

answer = str(
    question.get(
        "answer",
        ""
    )
).strip()

question_type = str(
    question.get(
        "question_type",
        ""
    )
).strip().lower()

difficulty = str(
    question.get(
        "difficulty",
        "medium"
    )
).strip().lower()

topic = str(
    question.get(
        "topic",
        ""
    )
).strip()

options = question.get(
    "options",
    {}
)

# Gemini may occasionally return options as a JSON string
if isinstance(options, str):

    try:
        options = json.loads(options)

    except Exception:
        options = {}

if not isinstance(options, dict):
    options = {}

normalized_options = {}

for key, value in options.items():

    letter = str(
        key
    ).strip().upper()

    if letter in [
        "A",
        "B",
        "C",
        "D",
        "E"
    ]:

        normalized_options[letter] = str(
            value
        ).strip()

# Detect question type automatically
if question_type not in [
    "multiple_choice",
    "true_false",
    "short_answer"
]:

    if len(normalized_options) >= 2:
        question_type = "multiple_choice"

    else:
        question_type = "short_answer"

# Validate difficulty
if difficulty not in [
    "easy",
    "medium",
    "hard"
]:

    difficulty = "medium"

return {
    "question": question_text,
    "options": normalized_options,
    "answer": answer,
    "question_type": question_type,
    "difficulty": difficulty,
    "topic": topic
}
```

# =========================================================

# GENERATE QUESTIONS WITH GEMINI

# =========================================================

def generate_questions(
textbook_text: str,
question_count: int,
difficulty: str,
question_type: str
):

```
if not gemini_client:

    raise Exception(
        "GEMINI_API_KEY is not configured."
    )

# Prevent an extremely large request
max_chars = 100000

if len(textbook_text) > max_chars:
    textbook_text = textbook_text[:max_chars]


# -----------------------------------------------------
# Question type instructions
# -----------------------------------------------------

if question_type == "multiple_choice":

    type_instruction = """
```

Create multiple-choice questions.

Each question must contain exactly four options:

A
B
C
D

The answer field must contain only:
A, B, C, or D.
"""

```
elif question_type == "true_false":

    type_instruction = """
```

Create True/False questions.

Use exactly these options:

A: True
B: False

The answer field must contain only:
A or B.
"""

```
else:

    type_instruction = """
```

Create short-answer questions.

The options object must be empty.

The answer field must contain the correct short answer.
"""

```
# -----------------------------------------------------
# Prompt
# -----------------------------------------------------

prompt = f"""
```

You are an expert educational test generator.

Create exactly {question_count} high-quality questions
based ONLY on the textbook content provided below.

Difficulty:
{difficulty}

Question type:
{question_type}

{type_instruction}

IMPORTANT RULES:

1. Use only information found in the textbook.
2. Do not invent facts.
3. Do not repeat questions.
4. Cover different sections and topics where possible.
5. Make questions clear and educational.
6. Do not provide explanations.
7. Do not include introductory text.
8. Return ONLY valid JSON.
9. Do not use Markdown.
10. Use English for all generated content.

Return this exact JSON structure:

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

TEXTBOOK CONTENT:

{textbook_text}
"""

```
# -----------------------------------------------------
# Gemini request
# -----------------------------------------------------

response = gemini_client.models.generate_content(
    model=GEMINI_MODEL,
    contents=prompt
)

raw_text = getattr(
    response,
    "text",
    ""
)

cleaned_text = clean_ai_response(
    raw_text
)

if not cleaned_text:

    raise Exception(
        "Gemini returned an empty response."
    )


# -----------------------------------------------------
# Parse JSON
# -----------------------------------------------------

try:

    data = json.loads(
        cleaned_text
    )

except Exception as error:

    print(
        "GEMINI RAW RESPONSE:",
        raw_text
    )

    raise Exception(
        "Could not parse Gemini response as JSON: "
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

if not isinstance(
    raw_questions,
    list
):

    raise Exception(
        "Gemini response does not contain a valid questions list."
    )


# -----------------------------------------------------
# Normalize
# -----------------------------------------------------

final_questions = []

for question in raw_questions:

    normalized = normalize_question(
        question
    )

    if normalized:
        final_questions.append(
            normalized
        )


if not final_questions:

    raise Exception(
        "Gemini did not generate valid questions."
    )


return final_questions
```

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

```
try:

    # -------------------------------------------------
    # Validate PDF
    # -------------------------------------------------

    if not pdf.filename:

        return {
            "success": False,
            "error": "No PDF file was uploaded."
        }


    if not pdf.filename.lower().endswith(
        ".pdf"
    ):

        return {
            "success": False,
            "error": "Please upload a PDF file."
        }


    # -------------------------------------------------
    # Question count
    # -------------------------------------------------

    question_count = max(
        10,
        min(
            int(question_count),
            40
        )
    )


    # -------------------------------------------------
    # Difficulty
    # -------------------------------------------------

    difficulty = (
        difficulty
        .strip()
        .lower()
    )

    if difficulty not in [
        "easy",
        "medium",
        "hard"
    ]:

        difficulty = "medium"


    # -------------------------------------------------
    # Question type
    # -------------------------------------------------

    question_type = (
        question_type
        .strip()
        .lower()
    )

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
    # Return result
    # -------------------------------------------------

    return {
        "success": True,
        "filename": pdf.filename,
        "pages": pages,
        "text_length": len(textbook_text),
        "question_count": len(questions),
        "difficulty": difficulty,
        "question_type": question_type,
        "questions": questions
    }


except Exception as error:

    print(
        "UPLOAD PDF ERROR:",
        repr(error)
    )

    return {
        "success": False,
        "error": str(error)
    }
```

# =========================================================

# SAVE EXAM

# =========================================================

@app.post("/save-exam")
async def save_exam(data: dict):

```
try:

    if not supabase:

        return {
            "success": False,
            "error": (
                "Supabase is not configured. "
                "Check SUPABASE_URL and SUPABASE_KEY."
            )
        }


    # -------------------------------------------------
    # Read frontend data
    # -------------------------------------------------

    title = str(
        data.get(
            "title",
            ""
        )
    ).strip()

    subject_id = data.get(
        "subject_id"
    )

    grade = data.get(
        "grade"
    )

    topic = str(
        data.get(
            "topic",
            ""
        )
    ).strip()

    exam_type = str(
        data.get(
            "exam_type",
            ""
        )
    ).strip()

    year = data.get(
        "year"
    )

    description = str(
        data.get(
            "description",
            ""
        )
    ).strip()

    file_url = str(
        data.get(
            "file_url",
            ""
        )
    ).strip()

    answer_url = str(
        data.get(
            "answer_url",
            ""
        )
    ).strip()

    questions = data.get(
        "questions",
        []
    )


    # -------------------------------------------------
    # Validate title
    # -------------------------------------------------

    if not title:

        return {
            "success": False,
            "error": "Exam title is required."
        }


    # -------------------------------------------------
    # Validate subject
    # -------------------------------------------------

    if subject_id is None:

        return {
            "success": False,
            "error": "Subject is required."
        }

    try:

        subject_id = int(
            subject_id
        )

    except Exception:

        return {
            "success": False,
            "error": "Invalid subject_id."
        }


    # -------------------------------------------------
    # Check subject
    # -------------------------------------------------

    subject_response = (
        supabase
        .table("subjects")
        .select("id")
        .eq(
            "id",
            subject_id
        )
        .limit(1)
        .execute()
    )


    if not subject_response.data:

        return {
            "success": False,
            "error": (
                "The selected subject does not exist."
            )
        }


    # -------------------------------------------------
    # Validate questions
    # -------------------------------------------------

    if not isinstance(
        questions,
        list
    ):

        return {
            "success": False,
            "error": "Questions must be a list."
        }


    if len(questions) == 0:

        return {
            "success": False,
            "error": (
                "There are no questions to save."
            )
        }


    # -------------------------------------------------
    # Prepare exam
    #
    # Only use columns that belong to the exams table.
    # -------------------------------------------------

    exam_row = {
        "title": title,
        "subject_id": subject_id,
        "grade": grade if grade else None,
        "topic": topic if topic else None,
        "exam_type": (
            exam_type
            if exam_type
            else None
        ),
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
        )
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
            "error": (
                "The exam could not be created."
            )
        }


    exam = exam_response.data[0]

    exam_id = exam.get(
        "id"
    )


    if exam_id is None:

        return {
            "success": False,
            "error": (
                "The exam was created, "
                "but no exam ID was returned."
            )
        }


    # -------------------------------------------------
    # Prepare questions
    # -------------------------------------------------

    question_rows = []


    for item in questions:

        normalized = normalize_question(
            item
        )

        if not normalized:
            continue


        question_rows.append({

            "exam_id": exam_id,

            "question":
                normalized["question"],

            "options":
                normalized["options"],

            "answer":
                normalized["answer"],

            "question_type":
                normalized["question_type"],

            "difficulty":
                normalized["difficulty"]

        })


    if not question_rows:

        return {
            "success": False,
            "error": (
                "No valid questions were found."
            ),
            "exam_id": exam_id
        }


    # -------------------------------------------------
    # Insert questions
    # -------------------------------------------------

    questions_response = (
        supabase
        .table("questions")
        .insert(question_rows)
        .execute()
    )


    if not questions_response.data:

        return {
            "success": False,
            "error": (
                "The exam was created, "
                "but the questions could not be saved."
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
            questions_response.data
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
```

# =========================================================

# GET QUESTIONS

# =========================================================

@app.get("/questions")
def get_questions(
exam_id: int
):

```
try:

    if not supabase:

        return {
            "success": False,
            "error": (
                "Supabase is not configured."
            )
        }


    response = (
        supabase
        .table("questions")
        .select(
            "id, exam_id, question, options, "
            "answer, difficulty, question_type, created_at"
        )
        .eq(
            "exam_id",
            exam_id
        )
        .order(
            "id"
        )
        .execute()
    )


    return {
        "success": True,
        "questions": response.data or []
    }


except Exception as error:

    print(
        "GET QUESTIONS ERROR:",
        repr(error)
    )

    return {
        "success": False,
        "error": str(error)
    }
```

# =========================================================

# GET EXAMS

# =========================================================

@app.get("/exams")
def get_exams(
subject_id: int | None = None,
grade: str | None = None,
search: str | None = None
):

```
try:

    if not supabase:

        return {
            "success": False,
            "error": (
                "Supabase is not configured."
            )
        }


    # -------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT use:
    #
    # subjects(name)
    #
    # because your database column is "Name".
    #
    # Instead, get exams first and load subjects
    # separately.
    # -------------------------------------------------

    query = (
        supabase
        .table("exams")
        .select("*")
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

        search_value = (
            search
            .strip()
        )

        if search_value:

            query = query.ilike(
                "title",
                f"%{search_value}%"
            )


    response = query.execute()

    exams = response.data or []


    # -------------------------------------------------
    # Load subjects
    # -------------------------------------------------

    subjects_response = (
        supabase
        .table("subjects")
        .select("id, Name")
        .execute()
    )

    subject_map = {}

    for subject in (
        subjects_response.data or []
    ):

        subject_map[
            subject.get("id")
        ] = subject.get(
            "Name"
        )


    # -------------------------------------------------
    # Add subject information
    # -------------------------------------------------

    for exam in exams:

        sid = exam.get(
            "subject_id"
        )

        exam["subject"] = {
            "id": sid,
            "name": subject_map.get(
                sid,
                "Unknown Subject"
            )
        }


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
```

# =========================================================

# GET SINGLE EXAM

# =========================================================

@app.get("/exams/{exam_id}")
def get_exam(
exam_id: int
):

```
try:

    if not supabase:

        return {
            "success": False,
            "error": (
                "Supabase is not configured."
            )
        }


    # -------------------------------------------------
    # Get exam
    # -------------------------------------------------

    exam_response = (
        supabase
        .table("exams")
        .select("*")
        .eq(
            "id",
            exam_id
        )
        .limit(1)
        .execute()
    )


    if not exam_response.data:

        return {
            "success": False,
            "error": "Exam not found."
        }


    exam = exam_response.data[0]


    # -------------------------------------------------
    # Get subject
    # -------------------------------------------------

    subject_id = exam.get(
        "subject_id"
    )

    if subject_id is not None:

        subject_response = (
            supabase
            .table("subjects")
            .select("id, Name")
            .eq(
                "id",
                subject_id
            )
            .limit(1)
            .execute()
        )

        if subject_response.data:

            subject = subject_response.data[0]

            exam["subject"] = {
                "id": subject.get("id"),
                "name": subject.get("Name")
            }


    # -------------------------------------------------
    # Get questions
    # -------------------------------------------------

    questions_response = (
        supabase
        .table("questions")
        .select(
            "id, exam_id, question, options, "
            "answer, difficulty, question_type, created_at"
        )
        .eq(
            "exam_id",
            exam_id
        )
        .order(
            "id"
        )
        .execute()
    )


    questions = (
        questions_response.data
        or []
    )


    return {
        "success": True,
        "exam": exam,
        "questions": questions
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
```

# =========================================================

# END

# =========================================================
