import streamlit as st
import datetime
import holidays
import tempfile
import os
from PyPDF2 import PdfMerger
from util import wrap_text_to_width, draw_wrapped_section, generate_pdf, convert_to_pdf, calculate_fbd, create_cover_sheet

def render_annual():
    annual_checkbox_descriptions = {
        "Performance standards did not permit the accurate evaluation of their job performance based on objective criteria related to their position.": {
            "articles": ["Article 12 Section 3, 5 U.S.C §§ 9508, 5 U.S.C. §§ 4302, 5 C.F.R. Part 430"],
            "argument": (
                "     Management is supposed to, to the maximum extent feasible, provide an accurate evaluation of an employee’s job performance based on objective criteria related to the position. By"
                " failing to do this, management has failed to follow the guidance provided through the National Agreement, Article 12 Section 3; 5 USC 4302; 5 USC 9508; 5 CFR Part 430. Each of these specify"
                ' instructions to how the appraisal system is to work. Each of these consistently state that an accurate evaluation must be provided to employees. 5 USC 4302 states "performance standards which'
                " will, to the maximum extent feasible, permit the accurate evaluation of job performance on the basis of objective criteria (which may include the extent of courtesy demonstrated to the public)"
                ' related to the job in question for each employee or position under the system." By not utilizing performance standards to provide an accurate evaluation, not only violates the employee’s rights'
                " granted under the National Agreement, but also violates the laws and regulations intended to protect federal employees from harm. By failing to utilize the performance standards to the degree at"
                " which they were intended to be used to evaluate an employee’s performance to provide an accurate evaluation of their work, management has failed to comply and created an unjust and unfair appraisal"
                " for this grievant and management needs to reconsider the appraisal score given."
            )
        },
        "Management was given specific distribution amounts per level of rating for employees.": {
            "articles": ["Article 12, Section 3, 5 C.F.R. Part 430.208, IRM 6.430.2.5.7"],
            "argument": (
                "     It is highly inappropriate for management to establish and distribute annual appraisals based upon specific distribution amounts per level of rating of employees. By utilizing this system"
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
            )
        },
        "Performance elements were not clearly defined": {
            "articles": ["Article 12 Section 3"],
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
    
    # --- Date and FBD input/display together ---
    if "date_received" not in st.session_state:
        st.session_state["date_received"] = datetime.date.today()

    st.header("Appraisal Grievance Intake")
    date_col, fbd_col = st.columns([1, 1])
    with date_col:
        date_received = st.date_input(
            "Date Received",
            value=st.session_state["date_received"],
            key="date_received",
            help="Date the appraisal was given to grievant."
        )
    with fbd_col:
        fbd = calculate_fbd(st.session_state["date_received"])
        st.info(f"🗕️ File By Date (15 business days): {fbd}")

    # --- FORM UI ---
    with st.form("grievance_form"):
        steward = st.text_input("Steward’s Name", key="Steward")
        grievant = st.text_input("Grievant’s Name", key="Grievant")
        years_list = [str(y) for y in range(2023, datetime.date.today().year + 2)]
        appraisal_year = st.selectbox("Appraisal Year", years_list, index=len(years_list)-1, key="appraisal_year")
        ratings = [f"{x:.1f}" for x in [i * 0.1 for i in range(10, 51)]]
        col1, col2 = st.columns(2)
        with col1:
            rating_received = st.selectbox("Current Rating", ratings, index=0, key="rating_received")
        with col2:
            previous_rating = st.selectbox("Prior Year’s Rating", ratings, index=0, key="previous_rating")

        case_id = st.text_input("Case Number")
        workarea = st.text_input("Work Area/ Operation")
        dept_man = st.text_input("Department Manager")
        flmanager = st.text_input("Frontline Manager")
        position = st.text_input("Title/Position")
        issue_description = str(st.text_area("Summary of Grievance", key="issue_description"))
        desired_outcome = str(st.text_area("Requested Resolution", key="desired_outcome"))

        uploaded_files = []
        MAX_UPLOADS = 10
        for i in range(MAX_UPLOADS):
            uploaded_files.append(
                st.file_uploader(
                    f"Supporting Document {i+1}",
                    type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
                    key=f"file_uploader_{i}",
                )
            )

        st.subheader("Alleged Violations")
        articles_set = set()
        arguments = []
        for desc, info in annual_checkbox_descriptions.items():
            checked = st.checkbox(desc, key=f"checkbox_{desc}")
            if checked:
                articles_set.update(info["articles"])
                arguments.append(info["argument"])

        submitted = st.form_submit_button("Generate Grievance PDF")

    # --- PDF Generation / Download ---
    if submitted:
        article_list = ", ".join(sorted(articles_set))
        full_argument = ""
        if arguments:
            full_argument = "\nThis grievance challenges the annual performance appraisal based on the following concerns:\n\n\n"
            for a in arguments:
                full_argument += f"{a}\n\n"

        filing_step = "Step Two - Annual Appraisal Grievance"

        # All fields for the cover sheet (in order)
        form_data = {
            "Step": filing_step,
            "Grievant": grievant,
            "Appraisal Year": appraisal_year,
            "Current Rating": rating_received,
            "Prior Year’s Rating": previous_rating,
            "Summary of Grievance": issue_description,
            "Requested Resolution": desired_outcome,
            "Date Received": str(st.session_state["date_received"]),
            "Articles of Violation": article_list,
            "Steward": steward,
            "Case ID": case_id,
            "Department Manager": dept_man,
            "Frontline Manager": flmanager,
            "Position": position,
            "Operation": workarea
        }

        # Only the fields you want in the main PDF, in order
        pdf_fields = {
            "Grievant": grievant,
            "Steward": steward,
            "Appraisal Year": appraisal_year,
            "Current Rating": rating_received,
            "Prior Year’s Rating": previous_rating,
            "Articles of Violation": article_list,
        }
        pdf_data = {k: form_data[k] for k in pdf_fields if k in form_data}

        grievance_type = st.session_state.get("grievance_type", "Annual Appraisal")
        cover_sheet_buffer = create_cover_sheet(form_data, grievance_type)  # Returns BytesIO
        base_pdf_buffer = generate_pdf(pdf_data, full_argument)            # Returns BytesIO

        # --- Merge PDFs: cover sheet first ---
        merger = PdfMerger()
        merger.append(cover_sheet_buffer)
        merger.append(base_pdf_buffer)

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
                            merger.append(f)
                    else:
                        converted_path = convert_to_pdf(file, filename)
                        if converted_path:
                            with open(converted_path, "rb") as f:
                                merger.append(f)
                except Exception as e:
                    st.warning(f"⚠️ Skipped {filename} due to error: {e}")

        output_name = f"{grievant.replace(' ', '_')}_{appraisal_year}_Argument.pdf"
        final_path = os.path.join(tempfile.gettempdir(), output_name)
        with open(final_path, "wb") as f:
            merger.write(f)
        merger.close()

        st.session_state.final_packet_path = final_path
        st.session_state.final_packet_name = output_name

    # --- Download button ---
    if "final_packet_path" in st.session_state and st.session_state.final_packet_path:
        with open(st.session_state.final_packet_path, "rb") as f:
            st.download_button("📅 Download Completed Grievance Packet", f, file_name=st.session_state.final_packet_name)
