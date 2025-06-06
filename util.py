import streamlit as st
import datetime
import holidays
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textwrap import wrap
from PyPDF2 import PdfMerger, PdfReader
from docx import Document as DocxDocument

WRAP_WIDTH = 120

def draw_wrapped_section(c, title, text, x, y, width, height, line_height):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, title)
    y -= line_height
    c.setFont("Helvetica", 10)
    for line in text.split('\n'):
        for wrapped in wrap(line, WRAP_WIDTH):
            if y < 50:
                c.showPage()
                y = height - 50
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

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "📄 Grievance Summary")
    y -= line_height * 2

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
    c.setFont("Helvetica", 10)

    try:
        if ext == ".txt":
            content = file.read().decode("utf-8").splitlines()
            for line in content:
                for wrapped in wrap(line, WRAP_WIDTH):
                    if y < 50:
                        c.showPage()
                        y = height - 50
                    c.drawString(x, y, wrapped)
                    y -= line_height
        elif ext == ".docx":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            doc = DocxDocument(tmp_path)
            for para in doc.paragraphs:
                for wrapped in wrap(para.text, WRAP_WIDTH):
                    if y < 50:
                        c.showPage()
                        y = height - 50
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
