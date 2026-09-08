from fastapi import FastAPI, UploadFile, File
import fitz

app = FastAPI()

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