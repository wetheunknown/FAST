import streamlit as st
import datetime
import holidays
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfMerger, PdfReader
from docx import Document as DocxDocument
from reportlab.pdfbase.pdfmetrics import stringWidth

def wrap_text_to_width(text, font_name, font_size, max_width):
    """
    Wrap a string so each line fits within max_width points.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def draw_wrapped_section(c, title, text, x, y, width, height, line_height):
    title_font = "Helvetica-Bold"
    title_size = 12
    body_font = "Helvetica"
    body_size = 10
    usable_width = width - 2 * x

    # Draw section title
    c.setFont(title_font, title_size)
    c.drawString(x, y, title)
    y -= line_height

    # Draw body text with proper wrapping and paragraph spacing
    c.setFont(body_font, body_size)
    for line in text.split('\n'):
        if line.strip() == "":
            y -= line_height  # Add extra space for blank lines (between paragraphs)
            continue
        wrapped_lines = wrap_text_to_width(line, body_font, body_size, usable_width)
        for wrapped in wrapped_lines:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont(title_font, title_size)
                c.drawString(x, y, title)
                y -= line_height
                c.setFont(body_font, body_size)
            c.drawString(x, y, wrapped)
            y -= line_height
    y -= line_height
    return y
    
def generate_pdf(data, argument):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    x, y = 50, height - 50
    line_height = 16

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "📄 Grievance Summary")
    y -= line_height * 2

    # Draw each section
    for key, value in data.items():
        y = draw_wrapped_section(c, f"{key}:", str(value), x, y, width, height, line_height)

    if argument:
        y = draw_wrapped_section(c, "Argument:", argument, x, y, width, height, line_height)

    c.save()
    return temp_file.name

def convert_to_pdf(file, filename):
    temp_pdf_path = os.path.join(tempfile.gettempdir(), f"converted_{filename}.pdf")
    ext = os.path.splitext(filename)[1].lower()
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    width, height = letter
    x, y = 50, height - 50
    line_height = 16
    body_font = "Helvetica"
    body_size = 10
    usable_width = width - 2 * x
    c.setFont(body_font, body_size)

    try:
        if ext == ".txt":
            content = file.read().decode("utf-8").splitlines()
            for line in content:
                wrapped_lines = wrap_text_to_width(line, body_font, body_size, usable_width)
                for wrapped in wrapped_lines:
                    if y < 50:
                        c.showPage()
                        y = height - 50
                        c.setFont(body_font, body_size)
                    c.drawString(x, y, wrapped)
                    y -= line_height
        elif ext == ".docx":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            doc = DocxDocument(tmp_path)
            for para in doc.paragraphs:
                wrapped_lines = wrap_text_to_width(para.text, body_font, body_size, usable_width)
                for wrapped in wrapped_lines:
                    if y < 50:
                        c.showPage()
                        y = height - 50
                        c.setFont(body_font, body_size)
                    c.drawString(x, y, wrapped)
                    y -= line_height
        elif ext in [".jpg", ".jpeg", ".png"]:
            img_path = os.path.join(tempfile.gettempdir(), filename)
            with open(img_path, "wb") as f:
                f.write(file.read())
            c.drawImage(img_path, x, y - 400, width=400, height=400)
            y -= 420
        else:
            return None

        c.save()
        return temp_pdf_path
    except Exception as e:
        st.warning(f"⚠️ Failed to convert {filename}: {e}")
        return None

def calculate_fbd(start_date):
    us_holidays = holidays.US()
    current_date = start_date
    business_days = 0
    while business_days < 15:
        current_date += datetime.timedelta(days=1)
        if current_date.weekday() < 5 and current_date not in us_holidays:
            business_days += 1
    return current_date
