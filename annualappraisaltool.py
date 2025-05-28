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

st.title("Federal Advocacy Support Toolkit \n FAST - Provided by NTEU CH. 66")

st.subheader("📌 Select Grievance Type")

grievance_type = st.radio(
    "Choose the type of grievance you'd like to file:",
    ["Annual Appraisal", "AWOL - Annual/Sick Leave", "Telework (Coming Soon)", "AWS (Soming Soon)", "Work Schedule/ Hours of Work (Coming Soon)"],
    index=0
)

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

if grievance_type == "Annual Appraisal":

    annual_checkbox_descriptions = {
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
        "articles": ["Article 12, Section 3, 5 C.F.R. Part 430.208, IRM 6.430.2.5.7"],
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
    st.header("Appraisal Grievance Intake")
    date_col, fbd_col = st.columns([1, 1])
    with date_col:
        date_received = st.date_input(
            "Date Received",
            value=datetime.date.today(),
            key="date_received",
            help="Date the appraisal was given to grievant."
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
        for desc, info in annual_checkbox_descriptions.items():
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

if grievance_type == "AWOL - Annual/Sick Leave":
    st.header("AWOL - Annual or Sick Leave Grievance Intake")

    # --- Date and FBD input/display together ---
    date_col, fbd_col = st.columns([1, 1])
    with date_col:
        date_received = st.date_input(
            "Date Received",
            value=datetime.date.today(),
            key="date_received",
            help="Date the AWOL notice was given to grievant."
        )
    with fbd_col:
        fbd = calculate_fbd(st.session_state["date_received"])
        st.info(f"🗕️ File By Date (15 business days): {fbd}")
        
    steward = st.text_input("Steward's Name")
    grievant = st.text_input("Grievant's Name")
    issue_description = st.text_area("Summary of Grievance", key="issue_description")
    desired_outcome = st.text_area("Requested Resolution", key="desired_outcome")

    st.subheader("Alleged Violations:\nAnnual Leave")

    # Define AWOL-related checkbox content
    awol_checkbox_descriptions = {
        "Annual Leave denied but no statement of reasoning provided after requested by the employee.": {
        "articles": ["Article 32 Section 1(A)(1)"],
        "argument": "     It is a violation of an employee's rights to deny annual leave without providing a statement of the reason(s) for the denial. Upon request, management should have provided"
            " the reasoning for denying the requested annual leave as laid out by the NA.\n"
        },
        "Issues with utilzing 15-min increments.": {
            "articles": ["Article 32 Section 1(A)(2)"],
            "argument": "     It is a violation of an employee's rights to charge or refuse to allow an employee to utilize their earned annual time in any increment outside of the allotted 15-minute"
            " increments as laid out by the NA.\n"
        },
        "Use or Lose - Employer provided confirmation in writing to employee of Use or Lose after management canceled requested Use or Lose.": {
            "articles": ["Article 32 Section 1(B)"],
            "argument": "     Upon management canceling the Use or Lose Annual Leave, they should have provided in writing the confirmation of the restoration. It is a violation of the employees'"
            " rights if management failed to do this after canceling the leave on the employee.\n"
        },
        "Conflict in requests but EOD order was not utilized.": {
            "articles": ["Article 32 Section 1(C)"],
            "argument": "     Management failed to follow the NA by failing to follow the EOD order on approval and denial of annual leave. An employee with a later EOD should have been given"
            " the requested leave over a newer EOD dated employee.\n"
        },
        "Annual leave request not timely responded to by management.": {
        "articles": ["Article 32 Section 1(D)"],
        "argument": "     It is a violation of an employee's rights as laid out by the NA for management to take an excessive amount of time to respond to a leave request. Management is supposed"
        " to make the denial or approval of a leave request in a timely manner to help facilitate an environment conducive with promoting a healthy work/life balance.\n"
        },
        "Employee's leave request was affected by another employee requesting time.": {
            "articles": ["Article 32 Section 2"],
            "argument": "     It is a violation of the employees' rights to allow for another employee requesting time off to affect another employee. Management should not change or"
            " adjust any other employees leave request based off of other employees request per the NA.\n"
        },
        "Use or Lose - Employer did not provide confirmation in writing to employee of Use or Lose after management canceled requested Use or Lose.": {
            "articles": ["Article 32 Section 1(B)"],
            "argument": "     Upon management canceling the Use or Lose Annual Leave, they should have provided in writing the confirmation of the restoration. It is a violation of the employees'"
            " rights if management failed to do this after canceling the leave on the employee.\n"
        },
        "Seasonal Employees - Placed in non-pay status for 10 days or less and was denied us of annual leave.": {
            "articles": ["Article 32 Section 3(A)"],
            "argument": "     It is inappropriate to not allow a seasonal employee in a non-pay status for less than 10 workdays to use their annual leave per the NA.\n"
        },
        "Seasonal Employees - Requested leave within the last 10 workdays of any fiscal year was denied based on anything except staffing and budgetary restrictions.": {
        "articles": ["Article 32 Section 3(B)"],
        "argument": "     Management could deny an annual leave request within the last 10 workdays of a fiscal year if it was related to staffing or budgetary restriction. Denying annual leave"
            " during this time frame for anything other than those is a violation of the employees' rights as laid out in the NA. \n"
        },
        "Seasonal Employees - Seasonal Employees leave requests are not being handled like a regular employees leave request would be.": {
            "articles": ["Article 32 Section 3(C)"],
            "argument": "     It is a violation of a seasonal employee's rights to not have annual leave treated the same as a non-probationary employee. Management is to treat seasonal employees"
            " annual leave requests the same as any other employee, even during peak season, per the NA.\n"
        },
        "The employee requested annual leave in advance for a religious holiday and it was not timely handled.": {
            "articles": ["Article 32 Section 4"],
            "argument": "     It is a violation of an employee's rights to not make every reasonable effort to approve requested annual leave for the purposes of a religious holiday as laid out in"
            " the NA. If workload and staffing needs were not an issue, the leave for this religious holiday should have been approved by management.\n"
        },
        "An employee was denied the opportunity to utilize annual leave or LWOP for a death in the immediate family.": {
            "articles": ["Article 32 Section 5"],
            "argument": "     Management should have approved any annual leave request or provided LWOP for up to 5 days for the death of an immediate family member. By failing to do so, management"
            " has failed to comply with the NA and has violated the employees' rights as laid out in the NA.\n"
        },
        "Employee was denied advanced annual and met the following conditions:\n"
        "  • Has less than 40 hours of advanced annual balance.\n"
        "  • Completed 1st year of probationary time.\n"
        "  • Been in current appointment for more than 90 days.\n"
        "  • Is eligible to earn annual leave.\n"
        "  • Did not request more advanced leave than could be earned during the remainder of the leave year.\n"
        "  • Is expected to return to work after having used the leave.": {
        "articles": ["Article 32 Section 6(A)"],
        "argument": f"     {grievant} met all the qualifications to be granted advanced annual leave. According to the NA, the employer will grant advanced annual if all the qualifications listed in"
            " the NA have been met. Management should have approved this advanced annual leave request because the employee qualified for it.\n"
        },
        "Denied additional advanced annual leave over the 40 hours limitation due to:\n"
        "  • A serious health condition.\n"
        "  • Or to care for a family member.": {
            "articles": ["Article 32 Section 6(B); Exhibit 33-1"],
            "argument": "     The NA lists that an exception to the rule of a max of 40 hours of advance annual leave if the employee or a family member is faced with a serious health condition."
            " Management should have approved the request for advanced annual leave based off the requirements listed in the NA.\n"
        },
        "The Agency failed to allow an employee to repay the balance due via earned annual leave or through a cash payment.": {
            "articles": ["Article 32 Section 6(C)"],
            "argument": "     It is a violation of an employee's rights to not allow an employee to repay the advanced annual any other way than described in the NA. Management should"
            f" allow {grievant} to pay back the amount borrowed for the advanced annual either by utilization of earned annual hours or through a cash payment.\n"
        },
        "The employer did not make every reasonable effort to approve advanced annual leave consistent with workload and staffing needs.": {
            "articles": ["Article 32 Section 6(D)"],
            "argument": "     Management failed to uphold the NA because every reasonable effort should have been made to grant the employees advanced annual leave consistent with the workload"
            " and staffing needs. By not following the NA on this, management created unjust harm and violated the employees' rights.\n"
        },
        "The employer granted advanced annual leave for one employee and denied another employee the right to use annual leave.": {
        "articles": ["Article 32 Section 6(D)"],
        "argument": "     Advanced annual is only to be approved after other employees' requests for annual leave have been considered. Failing to approve a request for annual leave for one"
            " employee but approving advanced annual leave for another is a violation of the NA and the employees' rights.\n"
        },
        "The employer failed to notify an employee of an AWOL charge in writing, no later than:"
        "  • The end of a pay period. \n"
        "  • Or 2 workdays from the end of the pay period. - If the AWOL charge occured during the last 2 days of the pay period (Friday or Saturday.)": {
            "articles": ["Article 32 Section 9"],
            "argument": "     Management failed to uphold the NA by failing to properly notify the employee of the AWOL charges. Management should have notified the employee by the end"
            " of the pay period. The exception to this is if the AWOL charges took place 2 days prior to the end of the pay period, either the week two Friday or Saturday of the pay period,"
            f" management is allotted an additional 2 workdays after the end of the pay period. By failing to do this according to the NA, management has caused undue and unjust harm to {grievant}\n"
        }
    }
    sick_awol_checkbox_descriptions = {
        "####Use or Lose - Employer provided confirmation in writing to employee of Use or Lose after management canceled requested Use or Lose.": {
            "articles": ["Article 32 Section 1(B)"],
            "argument": "     Upon management canceling the Use or Lose Annual Leave, they should have provided in writing the confirmation of the restoration. It is a violation of the employees'"
            " rights if management failed to do this after canceling the leave on the employee.\n"
        },
        "Conflict in requests but EOD order was not utilized.": {
            "articles": ["Article 32 Section 1(C)"],
            "argument": "     Management failed to follow the NA by failing to follow the EOD order on approval and denial of annual leave. An employee with a later EOD should have been given"
            " the requested leave over a newer EOD dated employee.\n"
        },
        "Annual leave request not timely responded to by management.": {
        "articles": ["Article 32 Section 1(D)"],
        "argument": "     It is a violation of an employee's rights as laid out by the NA for management to take an excessive amount of time to respond to a leave request. Management is supposed"
        " to make the denial or approval of a leave request in a timely manner to help facilitate an environment conducive with promoting a healthy work/life balance.\n"
        },
        "Employee's leave request was affected by another employee requesting time.": {
            "articles": ["Article 32 Section 2"],
            "argument": "     It is a violation of the employees' rights to allow for another employee requesting time off to affect another employee. Management should not change or"
            " adjust any other employees leave request based off of other employees request per the NA.\n"
        },
        "Use or Lose - Employer did not provide confirmation in writing to employee of Use or Lose after management canceled requested Use or Lose.": {
            "articles": ["Article 32 Section 1(B)"],
            "argument": "     Upon management canceling the Use or Lose Annual Leave, they should have provided in writing the confirmation of the restoration. It is a violation of the employees'"
            " rights if management failed to do this after canceling the leave on the employee.\n"
        },
        "Seasonal Employees - Placed in non-pay status for 10 days or less and was denied us of annual leave.": {
            "articles": ["Article 32 Section 3(A)"],
            "argument": "     It is inappropriate to not allow a seasonal employee in a non-pay status for less than 10 workdays to use their annual leave per the NA.\n"
        },
        "Seasonal Employees - Requested leave within the last 10 workdays of any fiscal year was denied based on anything except staffing and budgetary restrictions.": {
        "articles": ["Article 32 Section 3(B)"],
        "argument": "     Management could deny an annual leave request within the last 10 workdays of a fiscal year if it was related to staffing or budgetary restriction. Denying annual leave"
            " during this time frame for anything other than those is a violation of the employees' rights as laid out in the NA. \n"
        },
        "Seasonal Employees - Seasonal Employees leave requests are not being handled like a regular employees leave request would be.": {
            "articles": ["Article 32 Section 3(C)"],
            "argument": "     It is a violation of a seasonal employee's rights to not have annual leave treated the same as a non-probationary employee. Management is to treat seasonal employees"
            " annual leave requests the same as any other employee, even during peak season, per the NA.\n"
        },
        "The employee requested annual leave in advance for a religious holiday and it was not timely handled.": {
            "articles": ["Article 32 Section 4"],
            "argument": "     It is a violation of an employee's rights to not make every reasonable effort to approve requested annual leave for the purposes of a religious holiday as laid out in"
            " the NA. If workload and staffing needs were not an issue, the leave for this religious holiday should have been approved by management.\n"
        },
        "An employee was denied the opportunity to utilize annual leave or LWOP for a death in the immediate family.": {
            "articles": ["Article 32 Section 5"],
            "argument": "     Management should have approved any annual leave request or provided LWOP for up to 5 days for the death of an immediate family member. By failing to do so, management"
            " has failed to comply with the NA and has violated the employees' rights as laid out in the NA.\n"

                # Add all 43 violations from VBA here with descriptions and mapped arguments.
    }
    }

    selected_reasons = []
    selected_articles = []
    selected_arguments = []
    
    for desc, info in awol_checkbox_descriptions.items():
        checked = st.checkbox(desc, key=f"awol_checkbox_{desc}")
        if checked:
            selected_reasons.append(desc)
            selected_articles.extend(info["articles"])
            selected_arguments.append(info["argument"])
            
    st.subheader("Alleged Violations:\nSick Leave")
            
    for desc, info in sick_awol_checkbox_descriptions.items():
        checked = st.checkbox(desc, key=f"sick_awol_checkbox_{desc}")
        if checked:
            selected_reasons.append(desc)
            selected_articles.extend(info["articles"])
            selected_arguments.append(info["argument"])

    if st.button("Generate AWOL Grievance PDF"):
        if not steward or not grievant:
            st.warning("Please fill out all required fields.")
        else:
            full_argument = "\n\n".join(selected_arguments)
            article_list = ", ".join(sorted(set(selected_articles)))

            form_data = {
                "Steward": steward,
                "Grievant": grievant,
                "Issue Description": issue_description,
                "Desired Outcome": desired_outcome,
                "Articles of Violation": article_list
            }

            awol_pdf = generate_pdf(form_data, full_argument)

            with open(awol_pdf, "rb") as f:
                st.download_button("📄 Download AWOL Grievance PDF", f, file_name=f"{grievant.replace(' ', '_')}_AWOL_Grievance.pdf")
