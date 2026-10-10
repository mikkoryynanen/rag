from chonkie import Pipeline
from pypdf import PdfReader
from pathlib import Path
from src.services.database.database import get_job

UPLOAD_DIR = Path("data/uploads")

def chunk_document(path: str):
    pipe = Pipeline().chunk_with("recursive")

    reader = PdfReader(path)
    # TODO: No we get everything, select what we chunk?
    str = [page.extract_text() for page in reader.pages]

    docs = pipe.run(texts=str)

    return docs
