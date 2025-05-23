import streamlit as st
import datetime
import holidays
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textwrap import wrap
from PyPDF2 import PdfMerger

# Title
st.title("FAST – Federal Advocacy Support Toolkit")

# --- Form Section ---
st.header("Employee Appraisal Grievance Form")

# Session state reset
if st.button("🔄 Reset Form"):
    st.experimental_rerun()

# Form inputs
steward_name = st.text_input("Steward Name")
employee_name = st.text_input("Employee Name")

# Appraisal Year Dropdown (2023 to current or next depending on date)
today = datetime.date.today()
effective_year = today.year + 1 if today.month >= 10 else today.year
appraisal_year = st.selectbox("Appraisal Year", [str(y) for y in range(2023, effective_year + 1)])

# Ratings with 0.1 increments
ratings = [f"{x:.1f}" for x in [i * 0.1 for i in range(10, 51)]]
rating_received = st.selectbox("Rating Received", ratings)
previous_rating = st.selectbox("Previous Rating", ratings)

issue_description = st.text_area("Issue Description")
desired_outcome = st.text_area("Desired Outcome")
date_received = st.date_input("Date Received")

# --- File Upload Section ---
st.subheader("Upload Supporting Documents (up to 10)")
uploaded_files = [st.file_uploader(f"Upload file {i+1}", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"], key=f"file_uploader_{i}") for i in range(10)]

# --- Grievance Reasons with Articles and Arguments ---
st.subheader("Grievance Concerns")

checkbox_descriptions = {
    "Rating decreased without justification": {
        "articles": ["Article 21, Section 4"],
        "argument": "The rating was lowered without sufficient explanation or evidence, in violation of Article 21, Section 4, which requires ratings to be based on documented performance."
    },
    "Supervisor failed to communicate expectations": {
        "articles": ["Article 12, Section 3"],
        "argument": "The supervisor failed to clearly communicate performance expectations, as required under Article 12, Section 3."
    },
    "Performance elements were not clearly defined": {
        "articles": ["Article 21, Section 2"],
        "argument": "Performance elements were not defined in a manner that allowed the employee to understand what was expected, violating Article 21, Section 2."
    },
    "Employee was not given opportunity to improve": {
        "articles": ["Article 12, Section 7"],
        "argument": "The employee was not provided timely and constructive feedback or a reasonable opportunity to improve, contrary to Article 12, Section 7."
    },
    "Rating is inconsistent with prior feedback": {
        "articles": ["Article 21, Section 4"],
        "argument": "The rating is inconsistent with previous documented feedback and mid-year reviews, indicating a lack of justification under Article 21, Section 4."
    },
    "Rating is inconsistent with peer comparisons": {
        "articles": ["Article 21, Section 5"],
        "argument": "The rating is significantly lower than peers performing similar duties without justification, suggesting disparate treatment in violation of Article 21, Section 5."
    }
}

selected_reasons = []
articles_set = set()
arguments = []

st.write("Select applicable grievance reasons:")
for desc, info in checkbox_descriptions.items():
    if st.checkbox(desc):
        selected_reasons.append(desc)
        articles_set.update(info["articles"])
        arguments.append(info["argument"])

# File-by-date calculation (15 business days excluding weekends and holidays)
def calculate_fbd(start_date):
    us_holidays = holidays.US()
    current_date = start_date
    business_days = 0
    while business_days < 15:
        current_date += datetime.timedelta(days=1)
        if current_date.weekday() < 5 and current_date not in us_holidays:
            business_days += 1
    return current_date

# PDF Generation Function
def generate_pdf(data, argument):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    x, y = 50, height - 50
    line_height = 14

    def draw_wrapped_text(text):
        nonlocal y
        for line in text.split('\n'):
            for wrapped in wrap(line, 100):
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(x, y, wrapped)
                y -= line_height
            y -= line_height

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Grievance Summary")
    y -= 2 * line_height
    c.setFont("Helvetica", 10)

    for key, value in data.items():
        line = f"{key}: {value}"
        draw_wrapped_text(line)

    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Argument:")
    y -= line_height
    c.setFont("Helvetica", 10)
    draw_wrapped_text(argument)

    c.save()
    return temp_file.name

# Submit Button
if st.button("Submit Form"):
    fbd = calculate_fbd(date_received)

    generated_argument = "This grievance challenges the annual performance appraisal based on the following concerns:\n\n"
    for arg in arguments:
        generated_argument += f"- {arg}\n\n"

    article_list = ", ".join(sorted(articles_set))

    st.success("✅ Form Submitted Successfully!")
    st.write("**Steward:**", steward_name)
    st.write("**Employee:**", employee_name)
    st.write("**Appraisal Year:**", appraisal_year)
    st.write("**Rating Received:**", rating_received)
    st.write("**Previous Rating:**", previous_rating)
    st.write("**Issue Description:**")
    st.text(issue_description)
    st.write("**Desired Outcome:**")
    st.text(desired_outcome)
    st.write("**Date Received:**", str(date_received))
    st.write("**File By Date (15 business days):**", str(fbd))
    st.write("**Articles of Violation:**", article_list)
    st.write("---")
    st.write("**Generated Grievance Argument:**")
    st.text(generated_argument)

    # Generate base PDF
    form_data = {
        "Steward": steward_name,
        "Employee": employee_name,
        "Appraisal Year": appraisal_year,
        "Rating Received": rating_received,
        "Previous Rating": previous_rating,
        "Issue Description": issue_description,
        "Desired Outcome": desired_outcome,
        "Date Received": str(date_received),
        "File By Date": str(fbd),
        "Articles of Violation": article_list
    }
    base_pdf = generate_pdf(form_data, generated_argument)

    # Merge additional PDFs
    merger = PdfMerger()
    merger.append(base_pdf)

    for file in uploaded_files:
        if file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp.flush()
                merger.append(tmp.name)

    final_path = os.path.join(tempfile.gettempdir(), f"{employee_name.replace(' ', '_')}_{appraisal_year}_Argument.pdf")
    merger.write(final_path)
    merger.close()

    with open(final_path, "rb") as f:
        st.download_button("📄 Download PDF", f, file_name=os.path.basename(final_path))
