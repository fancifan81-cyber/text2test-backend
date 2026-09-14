import os
import json
import re

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import fitz

from google import genai
from supabase import create_client

# =========================================================

# ENVIRONMENT VARIABLES

# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

GEMINI_MODEL = os.getenv(
"GEMINI_MODEL",
"gemini-3.6-flash"
)

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
supabase = None

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
def root():

```
return {
    "success": True,
    "message": "Text2Test AI backend is running!"
}
```

# =========================================================

# HEALTH

# =========================================================

@app.get("/health")
def health():

```
return {
    "success": True,
    "gemini": bool(GEMINI_API_KEY),
    "supabase": bool(
        SUPABASE_URL and SUPABASE_KEY
    ),
    "model": GEMINI_MODEL
}
```

# =========================================================

# TEST SUPABASE

# =========================================================

@app.get("/test-supabase")
def test_supabase():

```
try:

    if not supabase:

        return {
            "success": False,
            "error": "Supabase is not configured."
        }

    result = (
        supabase
        .table("subjects")
        .select("id, Name")
        .limit(10)
        .execute()
    )

    return {
        "success": True,
        "subjects": result.data or []
    }

except Exception as e:

    print(
        "TEST SUPABASE ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
    }
```

# =========================================================

# GET SUBJECTS

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


    result = (
        supabase
        .table("subjects")
        .select("id, Name")
        .order("id")
        .execute()
    )


    subjects = []

    for item in result.data or []:

        subjects.append({
            "id": item.get("id"),
            "name": item.get("Name")
        })


    return {
        "success": True,
        "subjects": subjects
    }


except Exception as e:

    print(
        "GET SUBJECTS ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
    }
```

# =========================================================

# EXTRACT PDF

# =========================================================

def extract_pdf_text(pdf_data):

```
document = fitz.open(
    stream=pdf_data,
    filetype="pdf"
)

pages = len(document)

text = ""

for page in document:

    page_text = page.get_text()

    if page_text:
        text += page_text + "\n"


document.close()

return text.strip(), pages
```

# =========================================================

# CLEAN GEMINI JSON

# =========================================================

def clean_json(text):

````
if not text:
    return ""

text = text.strip()

# Remove ```json
text = re.sub(
    r"^```json\s*",
    "",
    text,
    flags=re.IGNORECASE
)

# Remove ```
text = re.sub(
    r"^```\s*",
    "",
    text
)

text = re.sub(
    r"\s*```$",
    "",
    text
)

text = text.strip()


# Find JSON object
start = text.find("{")
end = text.rfind("}")

if start >= 0 and end >= start:

    text = text[
        start:end + 1
    ]


return text.strip()
````

# =========================================================

# NORMALIZE QUESTION

# =========================================================

def normalize_question(item):

```
if not isinstance(item, dict):
    return None


question = str(
    item.get(
        "question",
        ""
    )
).strip()


if not question:
    return None


answer = str(
    item.get(
        "answer",
        ""
    )
).strip()


difficulty = str(
    item.get(
        "difficulty",
        "medium"
    )
).strip().lower()


if difficulty not in [
    "easy",
    "medium",
    "hard"
]:

    difficulty = "medium"


question_type = str(
    item.get(
        "question_type",
        "multiple_choice"
    )
).strip().lower()


if question_type not in [
    "multiple_choice",
    "true_false",
    "short_answer"
]:

    question_type = "multiple_choice"


options = item.get(
    "options",
    {}
)


if isinstance(options, str):

    try:

        options = json.loads(
            options
        )

    except Exception:

        options = {}


if not isinstance(options, dict):

    options = {}


clean_options = {}


for key, value in options.items():

    key = str(
        key
    ).strip().upper()


    if key in [
        "A",
        "B",
        "C",
        "D"
    ]:

        clean_options[key] = str(
            value
        ).strip()


return {
    "question": question,
    "options": clean_options,
    "answer": answer,
    "difficulty": difficulty,
    "question_type": question_type
}
```

# =========================================================

# GENERATE QUESTIONS

# =========================================================

def generate_questions(
textbook_text,
question_count,
difficulty,
question_type
):

```
if not gemini_client:

    raise Exception(
        "GEMINI_API_KEY is not configured."
    )


# Limit extremely large PDFs
textbook_text = textbook_text[:100000]


if question_type == "multiple_choice":

    instructions = """
```

Create multiple-choice questions.

Each question must have exactly four options:
A, B, C, D.

The answer must be exactly one of:
A, B, C, D.
"""

```
elif question_type == "true_false":

    instructions = """
```

Create True/False questions.

Use exactly:

A = True
B = False

The answer must be A or B.
"""

```
else:

    instructions = """
```

Create short-answer questions.

Use an empty options object.

The answer must contain the correct short answer.
"""

```
prompt = f"""
```

You are an expert educational test generator.

Generate exactly {question_count} questions
from the textbook content below.

Difficulty:
{difficulty}

Question type:
{question_type}

{instructions}

IMPORTANT:

* Use only information from the textbook.
* Do not invent facts.
* Do not repeat questions.
* Write everything in English.
* Do not include explanations.
* Return ONLY valid JSON.
* Do not use Markdown.

Return this structure:

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
"difficulty": "{difficulty}",
"question_type": "{question_type}"
}}
]
}}

TEXTBOOK:

{textbook_text}
"""

```
response = gemini_client.models.generate_content(
    model=GEMINI_MODEL,
    contents=prompt
)


raw = getattr(
    response,
    "text",
    ""
)


cleaned = clean_json(
    raw
)


if not cleaned:

    raise Exception(
        "Gemini returned an empty response."
    )


try:

    data = json.loads(
        cleaned
    )

except Exception as e:

    print(
        "GEMINI RESPONSE:",
        raw
    )

    raise Exception(
        "Could not parse Gemini response: "
        + str(e)
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
        "Gemini did not return a questions list."
    )


questions = []


for item in raw_questions:

    normalized = normalize_question(
        item
    )

    if normalized:

        questions.append(
            normalized
        )


if not questions:

    raise Exception(
        "No valid questions were generated."
    )


return questions
```

# =========================================================

# UPLOAD PDF

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
    # File validation
    # -------------------------------------------------

    if not pdf.filename:

        return {
            "success": False,
            "error": "No PDF file uploaded."
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
            "error": "The PDF is empty."
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
                "Could not extract text from the PDF."
            )
        }


    # -------------------------------------------------
    # Generate
    # -------------------------------------------------

    questions = generate_questions(
        textbook_text,
        question_count,
        difficulty,
        question_type
    )


    # -------------------------------------------------
    # Response
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


except Exception as e:

    print(
        "UPLOAD ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
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
                "Supabase is not configured."
            )
        }


    # -------------------------------------------------
    # Read data
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

        subject_id = int(
            subject_id
        )

    except Exception:

        return {
            "success": False,
            "error": "Invalid subject ID."
        }


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
            "error": "There are no questions to save."
        }


    # -------------------------------------------------
    # Check subject
    # -------------------------------------------------

    subject_check = (
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


    if not subject_check.data:

        return {
            "success": False,
            "error": (
                "The selected subject does not exist."
            )
        }


    # -------------------------------------------------
    # Prepare exam
    #
    # ONLY columns confirmed in your database.
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
    # INSERT EXAM
    # -------------------------------------------------

    exam_result = (
        supabase
        .table("exams")
        .insert(exam_row)
        .execute()
    )


    if not exam_result.data:

        return {
            "success": False,
            "error": (
                "Supabase did not return "
                "the created exam."
            )
        }


    exam_id = exam_result.data[0].get(
        "id"
    )


    if exam_id is None:

        return {
            "success": False,
            "error": (
                "Exam was created but "
                "no exam ID was returned."
            )
        }


    # -------------------------------------------------
    # Prepare questions
    # -------------------------------------------------

    question_rows = []


    for item in questions:

        q = normalize_question(
            item
        )


        if not q:
            continue


        question_rows.append({

            "exam_id": exam_id,

            "question":
                q["question"],

            "options":
                q["options"],

            "answer":
                q["answer"],

            "difficulty":
                q["difficulty"],

            "question_type":
                q["question_type"]

        })


    if not question_rows:

        return {
            "success": False,
            "error": (
                "No valid questions to save."
            ),
            "exam_id": exam_id
        }


    # -------------------------------------------------
    # INSERT QUESTIONS
    # -------------------------------------------------

    question_result = (
        supabase
        .table("questions")
        .insert(question_rows)
        .execute()
    )


    if not question_result.data:

        return {
            "success": False,
            "error": (
                "Exam was created, "
                "but questions could not be saved."
            ),
            "exam_id": exam_id
        }


    # -------------------------------------------------
    # SUCCESS
    # -------------------------------------------------

    return {
        "success": True,
        "message": (
            "Exam and questions saved successfully!"
        ),
        "exam_id": exam_id,
        "questions_saved": len(
            question_result.data
        )
    }


except Exception as e:

    print(
        "SAVE EXAM ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
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


    result = (
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
        "questions": result.data or []
    }


except Exception as e:

    print(
        "GET QUESTIONS ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
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

        search = search.strip()

        if search:

            query = query.ilike(
                "title",
                "%" + search + "%"
            )


    result = query.execute()

    exams = result.data or []


    # -------------------------------------------------
    # Load subjects separately
    #
    # This avoids the old:
    # subjects_1.name does not exist
    # error.
    # -------------------------------------------------

    subjects_result = (
        supabase
        .table("subjects")
        .select("id, Name")
        .execute()
    )


    subject_map = {}


    for subject in (
        subjects_result.data or []
    ):

        subject_map[
            subject.get("id")
        ] = subject.get(
            "Name"
        )


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


except Exception as e:

    print(
        "GET EXAMS ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
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
    # Exam
    # -------------------------------------------------

    exam_result = (
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


    if not exam_result.data:

        return {
            "success": False,
            "error": "Exam not found."
        }


    exam = exam_result.data[0]


    # -------------------------------------------------
    # Subject
    # -------------------------------------------------

    subject_id = exam.get(
        "subject_id"
    )


    if subject_id is not None:

        subject_result = (
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


        if subject_result.data:

            subject = (
                subject_result.data[0]
            )


            exam["subject"] = {
                "id": subject.get("id"),
                "name": subject.get("Name")
            }


    # -------------------------------------------------
    # Questions
    # -------------------------------------------------

    questions_result = (
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
        "exam": exam,
        "questions": (
            questions_result.data or []
        )
    }


except Exception as e:

    print(
        "GET EXAM ERROR:",
        repr(e)
    )

    return {
        "success": False,
        "error": str(e)
    }
```
