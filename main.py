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

app = FastAPI(
title="Text2Test AI",
description="AI-powered test generator and shared test library",
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

# ENVIRONMENT VARIABLES

# =========================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not SUPABASE_URL:
raise RuntimeError("SUPABASE_URL is not set in environment variables")

if not SUPABASE_KEY:
raise RuntimeError("SUPABASE_KEY is not set in environment variables")

if not GEMINI_API_KEY:
raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

SUPABASE_URL = SUPABASE_URL.strip().strip('"').strip("'")
SUPABASE_KEY = SUPABASE_KEY.strip().strip('"').strip("'")
GEMINI_API_KEY = GEMINI_API_KEY.strip().strip('"').strip("'")

if not SUPABASE_URL.startswith("https://"):
raise RuntimeError("SUPABASE_URL must start with https://")

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

```
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
```

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

```
    return {
        "success": True,
        "role": result.data
    }

except Exception as e:
    return {
        "success": False,
        "error": str(e)
    }
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
# -----------------------------------------------------
# VALIDATE QUESTION COUNT
# -----------------------------------------------------

question_count = max(
    10,
    min(question_count, 40)
)


# -----------------------------------------------------
# VALIDATE DIFFICULTY
# -----------------------------------------------------

if difficulty not in [
    "easy",
    "medium",
    "hard"
]:
    difficulty = "medium"


# -----------------------------------------------------
# VALIDATE QUESTION TYPE
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

        page_text = page.get_text()

        if page_text:
            text += page_text

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
        "message": (
            "Could not extract text from this PDF. "
            "Please make sure the PDF contains selectable text."
        )
    }


# =====================================================
# QUESTION FORMAT
# =====================================================

if question_type == "multiple_choice":

    format_instruction = """
```

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

```
elif question_type == "true_false":

    format_instruction = """
```

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

```
else:

    format_instruction = """
```

Each question must have exactly this structure:

{
"question": "Question text",
"options": {},
"answer": "Short correct answer"
}
"""

```
# =====================================================
# DIFFICULTY
# =====================================================

difficulty_instruction = {
    "easy": "Test basic facts and understanding.",
    "medium": "Test understanding and application.",
    "hard": (
        "Require deeper reasoning, comparison, "
        "analysis, or application."
    )
}.get(
    difficulty,
    "Test understanding and application."
)


# =====================================================
# GEMINI PROMPT
# =====================================================

prompt = f"""
```

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
7. All answer choices must be in ENGLISH.
8. All answers must be in ENGLISH.
9. Difficulty level: {difficulty}.
10. {difficulty_instruction}
11. Question type: {question_type}.
12. Do not repeat questions.
13. Make incorrect options plausible.
14. Do not add information that is not supported by the textbook.

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
Do not add explanations.

TEXTBOOK CONTENT:

{text[:30000]}
"""

````
# =====================================================
# CALL GEMINI
# =====================================================

try:

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

            last_error = Exception(
                "Gemini returned an empty response."
            )

        except Exception as e:

            last_error = e

            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{repr(e)}"
            )

            if attempt < 2:

                wait_time = 5 * (attempt + 1)

                print(
                    f"Waiting {wait_time} seconds..."
                )

                time.sleep(wait_time)


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
        "message": f"AI generation failed: {str(e)}"
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


# ===============
````
