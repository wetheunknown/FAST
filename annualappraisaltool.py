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

# Constants
WRAP_WIDTH = 95
MAX_UPLOADS = 10

st.title("FAST – Federal Advocacy Support Toolkit")

if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

checkbox_descriptions = {
    "Rating decreased without justification": {
        "articles": ["Article 21, Section 4"],
        "argument": "The rating was lowered without sufficient explanation or evidence, in violation of Article 21, Section 4."
    },
    "Supervisor failed to communicate expectations": {
        "articles": ["Article 12, Section 3"],
        "argument": "The supervisor failed to clearly communicate performance expectations, as required under Article 12, Section 3."
    },
    "Performance elements were not clearly defined": {
        "articles": ["Article 21, Section 2"],
        "argument": "Performance elements were not clearly defined, violating Article 21, Section 2."
    },
    "Employee was not given opportunity to improve": {
        "articles": ["Article 12, Section 7"],
        "argument": "The employee was not given the opportunity to improve, violating Article 12, Section 7."
    },
    "Rating is inconsistent with prior feedback": {
        "articles": ["Article 21, Section 4"],
        "argument": "The rating is inconsistent with prior feedback, violating Article 21, Section 4."
    },
    "Rating is inconsistent with peer comparisons": {
        "articles": ["Article 21, Section 5"],
        "argument": "The rating is inconsistent with peer comparisons, violating Article 21, Section 5."
    }
}

def reset_form():
    # Text inputs
    st.session_state["steward_name"] = ""
    st.session_state["employee_name"] = ""
    st.session_state["issue_description"] = ""
    st.session_state["desired_outcome"] = ""

    # Set default year selectbox to current year as string
    st.session_state["appraisal_year"] = str(datetime.date.today().year)
    # Set default ratings (first option in ratings list)
    st.session_state["rating_received"] = "1.0"
    st.session_state["previous_rating"] = "1.0"

    # Date input
    st.session_state["date_received"] = datetime.date.today()

    # File uploaders
    for i in range(MAX_UPLOADS):
        st.session_state[f"file_uploader_{i}"] = None

    # Checkboxes
    for key in checkbox_descriptions:
        st.session_state[key] = False

    # Download state
    st.session_state.final_packet_path = None
    st.session_state.final_packet_name = None
    st.session_state.reset_triggered = True

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

# Initialize download state variables outside the form
if "final_packet_path" not in st.session_state:
    st.session_state.final_packet_path = None
if "final_packet_name" not in st.session_state:
    st.session_state.final_packet_name = None

# --- FORM UI ---
st.header("Appraisal Grievance Intake")
with st.form("grievance_form"):
    steward_name = st.text_input("Steward’s Name", key="steward_name")
    employee_name = st.text_input("Grievant’s Name", key="employee_name")
    years_list = [str(y) for y in range(2023, datetime.date.today().year + 2)]
    appraisal_year = st.selectbox("Appraisal Year", years_list, key="appraisal_year")
    ratings = [f"{x:.1f}" for x in [i * 0.1 for i in range(10, 51)]]
    col1, col2 = st.columns(2)
    with col1:
        rating_received = st.selectbox("Current Rating", ratings, key="rating_received")
    with col2:
        previous_rating = st.selectbox("Prior Year’s Rating", ratings, key="previous_rating")

    issue_description = st.text_area("Summary of Grievance", key="issue_description")
    desired_outcome = st.text_area("Requested Resolution", key="desired_outcome")
    date_received = st.date_input("Date Received", value=datetime.date.today(), key="date_received")

    uploaded_files = [st.file_uploader(f"Supporting Document {i+1}", type=["pdf", "docx", "txt", "jpg", "jpeg", "png"], key=f"file_uploader_{i}") for i in range(MAX_UPLOADS)]

    st.subheader("Alleged Violations")
    selected_reasons = []
    articles_set = set()
    arguments = []
    for desc, info in checkbox_descriptions.items():
        if st.checkbox(desc, key=desc):
            selected_reasons.append(desc)
            articles_set.update(info["articles"])
            arguments.append(info["argument"])

    if st.form_submit_button("Generate Grievance PDF"):
        article_list = ", ".join(sorted(articles_set))
        full_argument = "This grievance challenges the annual performance appraisal based on the following concerns:\n\n"
        for a in arguments:
            full_argument += f"- {a}\n\n"

        # REMOVE "File By Date" from the form_data dict
        form_data = {
            "Steward": steward_name,
            "Employee": employee_name,
            "Appraisal Year": appraisal_year,
            "Current Rating": rating_received,
            "Prior Year’s Rating": previous_rating,
            "Summary of Grievance": issue_description,
            "Requested Resolution": desired_outcome,
            "Date Received": str(date_received),
            "Articles of Violation": article_list
        }

        base_pdf = generate_pdf(form_data, full_argument)

        merger = PdfMerger()
        with open(base_pdf, "rb") as f:
            merger.append(f)

        for file in uploaded_files:
            if file is not None:
                filename = file.name
                ext = os.path.splitext(filename)[1].lower()
                try:
                    if ext == ".pdf":
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(file.read())
                            tmp.flush()
                        with open(tmp.name, "rb") as f:
                            PdfReader(f)
                        with open(tmp.name, "rb") as f:
                            merger.append(f)
                    else:
                        converted_path = convert_to_pdf(file, filename)
                        if converted_path:
                            with open(converted_path, "rb") as f:
                                merger.append(f)
                except Exception as e:
                    st.warning(f"⚠️ Skipped {filename} due to error: {e}")

        output_name = f"{employee_name.replace(' ', '_')}_{appraisal_year}_Argument.pdf"
        final_path = os.path.join(tempfile.gettempdir(), output_name)
        merger.write(final_path)
        merger.close()

        # Store for download outside the form
        st.session_state.final_packet_path = final_path
        st.session_state.final_packet_name = output_name

# ---- FBD INFO (OUTSIDE FORM, ALWAYS UPDATED) ----
if "date_received" in st.session_state and st.session_state["date_received"]:
    fbd = calculate_fbd(st.session_state["date_received"])
    st.info(f"🗕️ File By Date (15 business days): {fbd}")

if st.session_state.final_packet_path:
    with open(st.session_state.final_packet_path, "rb") as f:
        st.download_button("📅 Download Completed Grievance Packet", f, file_name=st.session_state.final_packet_name)

if st.button("Reset Form"):
    reset_form()
    st.experimental_rerun()
