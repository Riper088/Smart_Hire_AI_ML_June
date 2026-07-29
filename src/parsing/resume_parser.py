"""Extract text from PDF / DOCX / TXT."""

import pdfplumber
import docx

def extract_text_from_pdf(file_bytes) -> str:
    text = ""
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_bytes) -> str:
    doc = docx.Document(file_bytes)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extract_text(file_like, filename: str) -> str:
    """Extract text based on file extension."""
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_like)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_like)
    elif filename.lower().endswith(".txt"):
        return file_like.read().decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT.")
