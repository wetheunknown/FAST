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

WRAP_WIDTH = 95
MAX_UPLOADS = 10

st.title("FAST \n Federal Advocacy Support Toolkit - Provided by NTEU CH. 66")

checkbox_descriptions = {
    "Performance standards did not permit the accurate evaluation of their job performance based on objective criteria related to their position.": {
        "articles": ["Article 12 Section 3, 5 U.S.C §§ 9508, 5 U.S.C. §§ 4302, 5 C.F.R. Part 430"],
        "argument": "     Management is supposed to, to the maximum extent feasible, provide an accurate evaluation of an employee’s job performance based on objective criteria related to the position. By"
        " failing to do this, management has failed to follow the guidance provided through the National Agreement, Article 12 Section 3; 5 USC 4302; 5 USC 9508; 5 CFR Part 430. Each of these specify"
        ' instructions to how the appraisal system is to work. Each of these consistently state that an accurate evaluation must be provided to employees. 5 USC 4302 states "performance standards which'
        " will, to the maximum extent feasible, permit the accurate evaluation of job performance on the basis of objective criteria (which may include the extent of courtesy demonstrated to the public)"
        ' related to the job in question for each employee or position under the system." By not utilizing performance standards to provide an accurate evaluation, not only violates the employee’s rights'
        " granted under the National Agreement, but also violates the laws and regulations intended to protect federal employees from harm. By failing to utilize the performance standards to the degree at"
        " which they were intended to be used to evaluate an employee’s performance to provide an accurate evaluation of their work, management has failed to comply and created an unjust and unfair appraisal"
        " for this grievant and management needs to reconsider the appraisal score given."
    },
    "Management was given specific distribution amounts per level of rating for employees.": {
        "articles": ["Article 12, Section 3"],
        "argument": "     It is highly inappropriate for management to establish and distribute annual appraisals based upon specific distribution amounts per level of rating of employees. By utilizing this system"
        " of restricting the amount allowed per level of rating, management removes the ability for employees to be fairly and accurately rated upon their performance over the year the annual appraisal period"
        ' covers. IRM 6.430.2.5.7 states "Presumptive ratings, for ratings of record, are prohibited by 5 CFR Section 430.208 (a)(2).” It then goes on to say “A rating of record can be based only on the'
        " evaluation of actual job performance for the designated performance appraisal period. A supervisor must not issue a rating of record that assumes a level of performance by an employee without an"
        ' actual evaluation of that employee’s performance.” Not only is this addressed in the IRM but it is also addressed in C.F.R Part 430.208, which states “The method for deriving and assigning a summary'
        " level may not limit or require the use of particular summary levels (i.e., establish a forced distribution of summary levels). However, methods used to make distinctions among employees or groups of"
        " employees such as comparing, categorizing, and ranking employees or groups on the basis of their performance may be used for purposes other than assigning a summary level including, but not limited"
        ' to, award determinations and promotion decisions.” By not following the guidance provided through the CFR, the Agency is not only violating the National Agreement, the IRM’s, but is also breaking the'
        " law by forcing a set distribution list per level of rating. Management has violated the employee’s rights by failing to provide an accurate reflection upon their service over the last appraisal"
        " period of a year and by utilization of a forced distribution of levels of rating. Management should only utilize the employee’s performance during the period of review and any variation from such"
        " is violating the laws and regulations in place to prevent harm."
    },
    "Performance elements were not clearly defined": {
        "articles": ["Article 12 Section 3, 5 C.F.R. Part 430.208, IRM 6.430.2.5.7"],
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

# --- Date and FBD input/display together ---
st.header("Appraisal Grievance Intake")
date_col, fbd_col = st.columns([1, 1])
with date_col:
    date_received = st.date_input(
        "Date Received",
        value=datetime.date.today(),
        key="date_received",
        help="Date you received the appraisal."
    )
with fbd_col:
    fbd = calculate_fbd(st.session_state["date_received"])
    st.info(f"🗕️ File By Date (15 business days): {fbd}")

# --- FORM UI ---
with st.form("grievance_form"):
    steward_name = st.text_input("Steward’s Name", key="steward_name")
    employee_name = st.text_input("Grievant’s Name", key="employee_name")
    years_list = [str(y) for y in range(2023, datetime.date.today().year + 2)]
    appraisal_year = st.selectbox("Appraisal Year", years_list, index=len(years_list)-1, key="appraisal_year")
    ratings = [f"{x:.1f}" for x in [i * 0.1 for i in range(10, 51)]]
    col1, col2 = st.columns(2)
    with col1:
        rating_received = st.selectbox("Current Rating", ratings, index=0, key="rating_received")
    with col2:
        previous_rating = st.selectbox("Prior Year’s Rating", ratings, index=0, key="previous_rating")

    issue_description = st.text_area("Summary of Grievance", key="issue_description")
    desired_outcome = st.text_area("Requested Resolution", key="desired_outcome")

    uploaded_files = []
    for i in range(MAX_UPLOADS):
        uploaded_files.append(
            st.file_uploader(
                f"Supporting Document {i+1}",
                type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
                key=f"file_uploader_{i}",
            )
        )

    st.subheader("Alleged Violations")
    selected_reasons = []
    articles_set = set()
    arguments = []
    for desc, info in checkbox_descriptions.items():
        checked = st.checkbox(desc, key=f"checkbox_{desc}")
        if checked:
            selected_reasons.append(desc)
            articles_set.update(info["articles"])
            arguments.append(info["argument"])

    submitted = st.form_submit_button("Generate Grievance PDF")

# --- PDF Generation / Download ---
if submitted:
    article_list = ", ".join(sorted(articles_set))
    # Only include argument section if something was checked
    full_argument = ""
    if arguments:
        full_argument = "\nThis grievance challenges the annual performance appraisal based on the following concerns:\n\n\n"
        for a in arguments:
            full_argument += f"{a}\n\n"

    form_data = {
        "Steward": steward_name,
        "Employee": employee_name,
        "Appraisal Year": appraisal_year,
        "Current Rating": rating_received,
        "Prior Year’s Rating": previous_rating,
        "Summary of Grievance": issue_description,
        "Requested Resolution": desired_outcome,
        "Date Received": str(st.session_state["date_received"]),
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

    st.session_state.final_packet_path = final_path
    st.session_state.final_packet_name = output_name

# --- Download button ---
if "final_packet_path" in st.session_state and st.session_state.final_packet_path:
    with open(st.session_state.final_packet_path, "rb") as f:
        st.download_button("📅 Download Completed Grievance Packet", f, file_name=st.session_state.final_packet_name)
