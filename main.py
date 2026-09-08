```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz

app = FastAPI()

# Cho phép frontend gọi backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Text2Test AI backend is running!"
    }


@app.post("/upload-pdf")
async def upload_pdf(pdf: UploadFile = File(...)):

    pdf_data = await pdf.read()

    document = fitz.open(
        stream=pdf_data,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    return {
        "filename": pdf.filename,
        "pages": len(document),
        "text_length": len(text),
        "text": text[:5000]
    }
```
