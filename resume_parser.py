import PyPDF2
import docx

def extract_text_from_file(file):
    """Extract text from a PDF or DOCX file."""
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = " ".join([page.extract_text() for page in pdf_reader.pages])
    elif file.filename.endswith('.docx'):
        doc = docx.Document(file)
        text = " ".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")
    return text
