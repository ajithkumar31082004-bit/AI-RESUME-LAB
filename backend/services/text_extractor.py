"""
AI RESUME LAB — Text Extractor Service
Extracts text from PDF, DOCX, and TXT files with robust fallbacks.
Parses key resume sections (Summary, Skills, Experience, Education, Projects).
"""
import os
import re
import io
import zipfile
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_stream_or_path) -> str:
    """Extract text from PDF using pypdf or pdfminer, with pure-python fallback."""
    text = ""
    # Try pypdf / PyPDF2
    try:
        import pypdf
        reader = pypdf.PdfReader(file_stream_or_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.debug(f"pypdf extraction failed or not installed: {e}")

    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        if isinstance(file_stream_or_path, (str, os.PathLike)):
            text = pdfminer_extract(file_stream_or_path)
        else:
            if hasattr(file_stream_or_path, "seek"):
                file_stream_or_path.seek(0)
            text = pdfminer_extract(file_stream_or_path)
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.debug(f"pdfminer extraction failed or not installed: {e}")

    # Fallback: simple text stream scan for plain text streams in PDF
    try:
        if isinstance(file_stream_or_path, (str, os.PathLike)):
            with open(file_stream_or_path, "rb") as f:
                raw_bytes = f.read()
        else:
            if hasattr(file_stream_or_path, "seek"):
                file_stream_or_path.seek(0)
            raw_bytes = file_stream_or_path.read()

        # Extract ASCII printable strings from streams
        text_matches = re.findall(rb"\(([^\(\)\\]{3,})\)", raw_bytes)
        if text_matches:
            extracted = " ".join([m.decode("latin1", errors="ignore") for m in text_matches])
            if len(extracted) > 100:
                return extracted
    except Exception as e:
        logger.warning(f"Raw PDF regex extraction failed: {e}")

    return text.strip()


def extract_text_from_docx(file_stream_or_path) -> str:
    """Extract text from DOCX using python-docx or zipfile/xml fallback."""
    try:
        import docx
        doc = docx.Document(file_stream_or_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        return "\n".join(full_text).strip()
    except Exception as e:
        logger.debug(f"python-docx extraction failed or not installed: {e}")

    # Fallback: unzip word/document.xml directly without extra dependencies
    try:
        if hasattr(file_stream_or_path, "seek"):
            file_stream_or_path.seek(0)
        with zipfile.ZipFile(file_stream_or_path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            # Find all <w:t> elements
            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            texts = []
            for node in tree.findall(".//w:t", namespaces):
                if node.text:
                    texts.append(node.text)
            return "\n".join(texts).strip()
    except Exception as e:
        logger.warning(f"DOCX XML zip extraction failed: {e}")

    return ""


def extract_text_from_txt(file_stream_or_path) -> str:
    """Extract text from plain text file or stream."""
    if isinstance(file_stream_or_path, (str, os.PathLike)):
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                with open(file_stream_or_path, "r", encoding=enc) as f:
                    return f.read().strip()
            except UnicodeDecodeError:
                continue
        return ""
    else:
        if hasattr(file_stream_or_path, "seek"):
            file_stream_or_path.seek(0)
        raw = file_stream_or_path.read()
        if isinstance(raw, bytes):
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    return raw.decode(enc).strip()
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", errors="ignore").strip()
        return str(raw).strip()


def extract_resume_text(file_obj, filename: str) -> str:
    """Dispatcher to extract text based on file extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return extract_text_from_pdf(file_obj)
    elif ext in ["docx", "doc"]:
        return extract_text_from_docx(file_obj)
    elif ext in ["txt", "md"]:
        return extract_text_from_txt(file_obj)
    else:
        # Attempt plain text read as fallback
        return extract_text_from_txt(file_obj)


def parse_resume_sections(text: str) -> dict:
    """
    Parses resume text into major sections:
    summary, skills, experience, education, projects, certifications, contact.
    """
    section_patterns = {
        "summary": r"(?:summary|professional summary|executive summary|about me|profile|objective)",
        "skills": r"(?:technical skills|skills & expertise|skills|core competencies|technologies|proficiencies)",
        "experience": r"(?:work experience|professional experience|employment history|experience|career history)",
        "education": r"(?:education|academic background|qualifications|degrees)",
        "projects": r"(?:projects|key projects|personal projects|portfolio)",
        "certifications": r"(?:certifications|licenses|credentials|courses)",
    }

    # Extract email and phone
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    github_match = re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)

    contact_info = {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
    }

    sections = {
        "contact": contact_info,
        "summary": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": "",
    }

    # Split text into lines and identify section headers
    lines = text.split("\n")
    current_section = None
    section_lines = {k: [] for k in sections if k != "contact"}

    for line in lines:
        clean_line = line.strip().lower()
        if len(clean_line) < 3:
            continue

        matched_section = None
        for sec, pat in section_patterns.items():
            if re.match(rf"^{pat}[:\s]*$", clean_line) or re.match(rf"^[#\*\-_\s]*{pat}[:\s]*$", clean_line):
                matched_section = sec
                break

        if matched_section:
            current_section = matched_section
        elif current_section:
            section_lines[current_section].append(line)

    for sec in section_lines:
        sections[sec] = "\n".join(section_lines[sec]).strip()

    return sections
