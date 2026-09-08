```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz

app = FastAPI()

# CORS: cho phép frontend gọi backend
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

    # Đọc file PDF
    pdf_data = await pdf.read()

    # Mở PDF
    document = fitz.open(
        stream=pdf_data,
        filetype="pdf"
    )

    # Lấy text từ PDF
    text = ""

    for page in document:
        text += page.get_text()

    # Đóng PDF
    document.close()

    return {
        "filename": pdf.filename,
        "pages": len(fitz.open(
            stream=pdf_data,
            filetype="pdf"
        )),
        "text_length": len(text),
        "text": text[:5000]
    }
```
