"""
parser.py
Extracts text from each file format.
Receives a FileInfo dict from loader.py.
Returns a Document dict with extracted text + metadata.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from src.logger import get_logger

logger = get_logger(__name__)

# ── Document shape ───────────────────────────────────────────────────────────
# Every parser function returns this same structure.
# Downstream components (chunker, embedder) always receive this shape.
def make_document(file_info: Dict[str, Any], text: str, extra_metadata: Optional[Dict] = None) -> Dict[str, Any]:
    doc = {
        "file_name":  file_info["file_name"],
        "extension":  file_info["extension"],
        "file_path":  str(file_info["file_path"]),
        "size_bytes": file_info["size_bytes"],
        "text":       text.strip(),
        "metadata":   extra_metadata or {},
    }
    return doc


# ── PDF ──────────────────────────────────────────────────────────────────────
def extract_pdf(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract text from PDF using PyMuPDF. Preserves page numbers."""
    import fitz  # PyMuPDF
    pages_text = []
    try:
        doc = fitz.open(str(file_info["file_path"]))
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text()
            if page_text.strip():
                pages_text.append(f"[Page {page_num}]\n{page_text}")
        doc.close()
    except Exception as e:
        logger.error(f"PDF extraction failed for {file_info['file_name']}: {e}")
    text = "\n\n".join(pages_text)
    return make_document(file_info, text, {"page_count": len(pages_text)})


# ── DOCX ─────────────────────────────────────────────────────────────────────
def extract_docx(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract text from Word documents. Preserves paragraph order."""
    from docx import Document
    paragraphs = []
    try:
        doc = Document(str(file_info["file_path"]))
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
    except Exception as e:
        logger.error(f"DOCX extraction failed for {file_info['file_name']}: {e}")
    text = "\n\n".join(paragraphs)
    return make_document(file_info, text, {"paragraph_count": len(paragraphs)})


# ── TXT ──────────────────────────────────────────────────────────────────────
def extract_txt(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Read plain text files directly."""
    text = ""
    try:
        text = file_info["file_path"].read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"TXT extraction failed for {file_info['file_name']}: {e}")
    return make_document(file_info, text)


# ── MARKDOWN ─────────────────────────────────────────────────────────────────
def extract_markdown(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read markdown as plain text.
    We keep the raw markdown — headings (#, ##) are useful for
    structure-aware chunking in a later phase.
    """
    text = ""
    try:
        text = file_info["file_path"].read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Markdown extraction failed for {file_info['file_name']}: {e}")
    return make_document(file_info, text)

# ── CSV ───────────────────────────────────────────────────────────────────────
def extract_csv(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert CSV rows into readable text.
    Each row becomes: "column1: value1 | column2: value2"
    This makes tabular data searchable as natural language.
    """
    import pandas as pd
    rows_text = []
    try:
        df = pd.read_csv(str(file_info["file_path"]))
        for _, row in df.iterrows():
            row_str = " | ".join(f"{col}: {val}" for col, val in row.items())
            rows_text.append(row_str)
    except Exception as e:
        logger.error(f"CSV extraction failed for {file_info['file_name']}: {e}")
    text = "\n".join(rows_text)
    return make_document(file_info, text, {"row_count": len(rows_text)})


# ── JSON ─────────────────────────────────────────────────────────────────────
def extract_json(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Convert JSON to formatted string for embedding."""
    import json
    text = ""
    try:
        data = json.loads(file_info["file_path"].read_text(encoding="utf-8"))
        text = json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"JSON extraction failed for {file_info['file_name']}: {e}")
    return make_document(file_info, text)


# ── NDJSON ───────────────────────────────────────────────────────────────────
def extract_ndjson(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    NDJSON = Newline-Delimited JSON.
    Each line is a separate JSON object (e.g. one support ticket per line).
    We extract each line separately and join them.
    """
    import json
    records = []
    try:
        lines = file_info["file_path"].read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if line:
                obj = json.loads(line)
                records.append(json.dumps(obj, indent=2))
    except Exception as e:
        logger.error(f"NDJSON extraction failed for {file_info['file_name']}: {e}")
    text = "\n\n---\n\n".join(records)
    return make_document(file_info, text, {"record_count": len(records)})


# ── YAML ─────────────────────────────────────────────────────────────────────
def extract_yaml(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Convert YAML to formatted string."""
    import yaml, json
    text = ""
    try:
        data = yaml.safe_load(file_info["file_path"].read_text(encoding="utf-8"))
        text = json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"YAML extraction failed for {file_info['file_name']}: {e}")
    return make_document(file_info, text)


# ── HTML ─────────────────────────────────────────────────────────────────────
def extract_html(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Strip HTML tags using BeautifulSoup, return clean text."""
    from bs4 import BeautifulSoup
    text = ""
    try:
        raw = file_info["file_path"].read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "lxml")
        text = soup.get_text(separator="\n")
    except Exception as e:
        logger.error(f"HTML extraction failed for {file_info['file_name']}: {e}")
    return make_document(file_info, text)


# ── ROUTER ───────────────────────────────────────────────────────────────────
# Maps each extension to its extraction function.
EXTRACTORS = {
    ".pdf":    extract_pdf,
    ".docx":   extract_docx,
    ".txt":    extract_txt,
    ".md":     extract_markdown,
    ".csv":    extract_csv,
    ".json":   extract_json,
    ".ndjson": extract_ndjson,
    ".yaml":   extract_yaml,
    ".yml":    extract_yaml,
    ".html":   extract_html,
}


def parse_file(file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Main entry point. Routes a FileInfo dict to the correct extractor.
    Returns a Document dict or None if the format is unsupported.
    """
    ext = file_info["extension"]
    extractor = EXTRACTORS.get(ext)

    if not extractor:
        logger.warning(f"No extractor for extension '{ext}': {file_info['file_name']}")
        return None

    logger.info(f"Parsing [{ext}]: {file_info['file_name']}")
    document = extractor(file_info)

    if not document["text"]:
        logger.warning(f"Empty text extracted from: {file_info['file_name']}")

    return document
