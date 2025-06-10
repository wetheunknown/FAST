import streamlit as st
import datetime
import holidays
import tempfile
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
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
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
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
    buffer.seek(0)
    return buffer
    
def convert_to_pdf(file, filename):
    temp_pdf_path = os.path.join(tempfile.gettempdir(), f"converted_{filename}.pdf")
    ext = os.path.splitext(filename)[1].lower()
    c = canvas.Canvas(temp_pdf_path, pagesize=LETTER)
    width, height = LETTER
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
            from docx import Document as DocxDocument
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
        # Return as BytesIO for consistency
        with open(temp_pdf_path, "rb") as pdf_file:
            buffer = BytesIO(pdf_file.read())
        buffer.seek(0)
        return buffer
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

def create_cover_sheet(form_data, grievance_type):
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import LETTER
    import datetime

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 72, f"{grievance_type} Filing Cover Sheet")

    c.setFont("Helvetica", 12)
    y = height - 120
    line_height = 24
    label_x = 72
    value_x = 200

    # Add fields
    fields = [
        ("Date of Filing", datetime.datetime.now().strftime("%Y-%m-%d")),
        ("Case ID", form_data.get("Case ID", "N/A")),
        ("Grievant", form_data.get("Grievant", "")),
        ("Steward", form_data.get("Steward", "")),
        ("Issue Description", form_data.get("Issue Description", "")),
        ("Articles of Violation", form_data.get("Articles of Violation", "")),
        ("Desired Outcome", form_data.get("Desired Outcome", "")),
    ]

    # Simple text wrap for values that are too long
    def wrap_text(text, font_name, font_size, max_width):
        lines = []
        if not text:
            return [""]
        words = text.split()
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + " " + word
            if c.stringWidth(test_line, font_name, font_size) > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        lines.append(current_line)
        return lines

    value_max_width = width - value_x - 72  # 72pt margin on right

    for label, value in fields:
        c.drawString(label_x, y, f"{label}:")
        wrapped_lines = wrap_text(str(value), "Helvetica", 12, value_max_width)
        for i, line in enumerate(wrapped_lines):
            c.drawString(value_x, y - i * line_height, line)
        y -= line_height * max(1, len(wrapped_lines))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def merge_pdfs(cover_buffer, main_buffer):
    cover_buffer.seek(0)
    main_buffer.seek(0)
    cover_reader = PdfReader(cover_buffer)
    main_reader = PdfReader(main_buffer)
    writer = PdfWriter()

    writer.add_page(cover_reader.pages[0])
    for page in main_reader.pages:
        writer.add_page(page)

    output_buffer = BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer
