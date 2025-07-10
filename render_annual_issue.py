import streamlit as st
import datetime
import holidays
import tempfile
import os
from io import BytesIO
from PyPDF2 import PdfMerger
from util import wrap_text_to_width, draw_wrapped_section, generate_pdf, convert_to_pdf, calculate_fbd, create_cover_sheet, merge_pdfs

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
        "Employee was not given their annual appraisal on the 6850-BU.": {
            "articles": ["Article 12 Section 4, 5 C.F.R § 430.208"],
            "argument": "Management is meant to keep annual appraisals fair across the Agency. This helps to ensure that employees are treated fairly during the review process. This begins with the"
            " utilization of the form 6850-BU, which allows for the same information to be applied in a strategic way to showcase the employee’s accomplishments and areas of concern over the annual appraisal"
            " year being evaluated. By management choosing to perform the annual appraisal on anything other than the 6850-BU form, it is highly inappropriate and creates unfair and unjust representation for"
            " the employee's appraisal. The form is meant to be utilized by all of management and by choosing to not follow this guidance, management has caused undue harm to the employee and needs to"
            " reevaluate the employee utilizing the correct form to ensure that the appraisal is a fair appraisal for the employee’s appraisal year being evaluated. "
        },
        "Rating was given outside of rating period based on the ending of my social security number. ": {
            "articles": ["Article 12, Section 4, Exhibit 12-2, 5 USC Chapter 43, 5307(d), 5 CFR 430.208 (a) (1), (h), IRM 6.430.3.5.1.1, IRM 6.430.2.4.2, IRM 6.430.2.4.2.1, Document 11678"],
            "argument": "This grievance concerns the current policy of determining the annual performance appraisal period based on the last digit of an employee’s Social Security Number (SSN). Under this"
            " policy, employees receive their annual performance appraisals in different months throughout the fiscal year, resulting in varying evaluation periods. This practice creates inconsistencies in"
            " performance assessment and may lead to inequities in how employees are rated and rewarded. Specifically, employees in similar positions are subject to different performance periods"
            " (e.g., October–September versus June–May), potentially affecting fairness in evaluations, award eligibility, and advancement opportunities. Under 5 CFR § 430.206(b), federal agencies are required"
            " to ensure consistency and fairness in performance appraisals. Management has failed to comply with the guidance issued regarding the annual appraisals and how they are to be performed. Management"
            " needs to reevaluate this annual appraisal and use the guidance given to ensure that a consistent and fair performance evaluation is issued to the employee."
        },
        "Employee changed from one permanent position to another within the last 60 days of the appraisal year and the departure appraisal was not used for the rating of record.": {
            "articles": ["Article 12, Section 4, IRM 6.430.2.4.2, IRM 6.430.2.4.2.1, 5 C.F.R § 430.208"],
            "argument": "When an employee permanently changes positions within the last 60 days of the appraisal year, the departing supervisor is required to complete a departure appraisal, which must then be"
            " used as the basis for the employee's rating of record. In this case, the failure to use the departure appraisal violates 5 C.F.R. § 430.208(a), which mandates that performance be appraised by the"
            " supervisor who had oversight during the relevant appraisal period. Ignoring the departure appraisal removes accountability from the supervisor who observed the employee’s performance for the"
            " majority of the year and places the burden unfairly on a new supervisor with limited observation time. Instead, management should have ensured that the departure appraisal was properly completed"
            " and submitted as the rating of record. Moving forward, all supervisors must be reminded of their responsibility to complete departure appraisals during personnel moves and management must track"
            " such transitions to ensure compliance. A system-level alert or checklist should be implemented to prevent oversight when an employee changes positions near the end of an appraisal period. "
        },
        "Departing supervisor did not comply by performing a departure appraisal.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "When a supervisor leaves their position—regardless of whether the departure is permanent or temporary—they are required to complete a departure appraisal for any employee they"
            " supervised for at least 60 days in the appraisal period. In this case, the supervisor failed to fulfill that obligation, which directly contradicts Article 12 of the National Agreement and 5"
            " C.F.R. § 430.208(b). This creates a gap in documentation and can lead to an inaccurate or incomplete appraisal of the employee’s performance, especially if the incoming supervisor has not"
            " observed the employee’s work long enough to fairly evaluate it. The supervisor should have completed and submitted the departure appraisal before leaving their position, with clear documentation"
            " of the observed performance. To correct this moving forward, management should enforce a departure appraisal checklist for all exiting supervisors and tie its completion to the supervisor's"
            " departure clearance process. Training sessions and reminders should be issued to all management personnel to ensure they understand their obligations under the performance management system. "
        },
        "Supervisor departed from their position during the last 60 days of the appraisal period, and the departure appraisal was not used.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "When a supervisor leaves during the final 60 days of an appraisal period, their departure appraisal must be used as the employees' rating of record if the incoming supervisor has not"
            " observed the employee for the minimum 60-day requirement. In this situation, failing to use the departure appraisal violates both 5 C.F.R. § 430.207 and Article 12 of the National Agreement, as"
            " the appraisal must be based on observed performance by a qualified rater. Instead, relying on an incoming supervisor who lacks sufficient observation time results in an invalid and potentially"
            " grievable rating of record. What should have occurred is that the departing supervisor completes the appraisal, and that rating is used without further modification. Management must implement a"
            " performance appraisal tracking system that flags when supervisors are departing near the end of the appraisal cycle, ensuring that appropriate appraisals are completed and used. A compliance audit"
            " of recent supervisor departures should also be considered to identify and rectify any additional oversights."
        },
        "Supervisor temporarily departed their position during the last 60 days of the employee's appraisal period, but this supervisor did not perform the appraisal.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Even in cases of temporary departure, supervisors who have observed an employee’s performance for at least 60 days in the appraisal period are still responsible for completing a"
            " departure appraisal if they are unavailable during the close of the cycle. In this instance, the failure to conduct an appraisal results in a rating being issued by a manager who did not meet the"
            " observation requirement, violating 5 C.F.R. § 430.208 and the performance appraisal provisions of the National Agreement. An appraisal must be based on actual performance, and that requires"
            " firsthand knowledge from the observing supervisor. Instead, the departing supervisor should have completed the appraisal before leaving or coordinated its completion remotely, if appropriate."
            " To avoid recurrence, management must implement a notification protocol to flag when temporary reassignments or absences intersect with appraisal responsibilities. Clear expectations and"
            " accountability measures should be communicated to all managers, especially during the final quarter of the appraisal period."
        },
        "Supervisor left their position between the 5th and 7th month of the appraisal period, the employees management chain did not utilize the departing appraisal for the employees mid-year review.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "When a supervisor leaves midway through an appraisal year, particularly between the 5th and 7th month, a departure appraisal should be completed and used to inform the employee’s"
            " mid-year review. Failing to incorporate this appraisal results in the new supervisor issuing feedback or mid-year evaluations without sufficient observation, which violates the principle of fair"
            " and meaningful performance evaluation. The departing supervisor had the necessary observation period and context to provide accurate feedback, and that appraisal should have been used as the"
            " foundation for the mid-year. Instead, the management chain ignored a key performance record, resulting in an incomplete review and undermining the appraisal process. Moving forward, management"
            " must ensure that all departure appraisals are properly routed and considered during mid-year reviews when the supervisor leaves mid-cycle. Internal procedures should be implemented to link"
            " mid-year reviews to any available departure appraisals to ensure continuity and accuracy. "
        },
        "Departure appraisal used to disadvantage the employee (e.g., denial of overtime, Telework, or AWS).": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "A departure appraisal, while important, is not a final rating of record and should not be used to take adverse actions against employees, such as denying overtime, Telework, or"
            " Alternative Work Schedules (AWS). When this occurs, it violates the National Agreement and OPM guidance, which clarify that departure appraisals are not final and are subject to further"
            " evaluation. Using them as the basis for punitive actions bypasses procedural safeguards and the opportunity for employee rebuttal, creating an unfair and potentially grievable situation. Instead,"
            " any action that disadvantages the employee must be based on finalized ratings or documented, reviewed misconduct—not interim evaluations. To correct this, managers must receive training that"
            " clearly distinguishes between different types of performance documentation and their appropriate use. Any prior actions taken based on a departure appraisal alone should be reviewed and reversed"
            " if improperly applied. "
        },
        "Departure appraisal improperly becoming a de facto rating of record.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208 "],
            "argument": "Departure appraisals are meant to document observed performance when a supervisor leaves, but they are not intended to serve as the final rating of record unless the departing"
            " supervisor has observed the employee for the full appraisal period or no other qualified supervisor is available. Improperly treating a departure appraisal as the rating of record undermines the"
            " integrity of the appraisal process, especially if there are months of performance not captured or reviewed. This mistake removes the chance for subsequent supervisors to observe, document, and"
            " provide input, and may result in an inaccurate performance rating. Instead, management should only use the departure appraisal as part of a complete evaluation or if required under 5 C.F.R. §"
            " 430.208. To prevent this issue in the future, supervisors must be educated on the conditions under which departure appraisals can and cannot be converted into ratings of record. Appraisal"
            " timelines and rater assignments should be monitored to ensure proper sequencing and compliance. "
        },
        "Departure appraisal not held until used in an annual rating.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Departure appraisals must be retained and not discarded until the employee's final annual rating of record is completed and any related grievance or appeal rights have expired. When"
            " a departure appraisal is not held for this purpose, it violates federal regulations and the National Agreement, which require all supporting documentation for appraisals to be maintained until"
            " no longer needed. Discarding the appraisal prematurely denies both the employee and future rating officials access to important documentation that may affect the employee’s final rating. Instead,"
            " the Employer must ensure all departure appraisals are stored securely and linked to the appropriate employee records. Moving forward, management should establish a mandatory retention schedule"
            " aligned with the performance management system and require electronic retention of all departure appraisals until the final rating of record and any related proceedings are complete. "
        },
        "Improper use of a recordation before a rating of record. ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Evaluative recordations, such as written feedback or monitored contact summaries, may only be used in a rating of record if shared with the employee within 15 workdays of the event and"
            " if the employee was given a chance to respond. Using a recordation that wasn’t disclosed or shared violates Article 12, Section 9 of the National Agreement and basic principles of due process. This"
            " undermines employee rights by denying them the opportunity to rebut or clarify performance events, which could unjustly influence the final rating. Instead, management should only use recordations"
            " that comply fully with notification and response requirements. To correct this, managers should audit all recordations used in ratings and discard any that do not meet notification rules."
            " Additionally, employees should be notified immediately of any recordation that may be used in a future rating to ensure transparency and fairness. "
        },
        "Appraisal period not extended when 60-day minimum not met.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Employees must be under the supervision of a rating official for a minimum of 60 days before a valid performance appraisal can be issued. If no supervisor meets that requirement during"
            " the appraisal period, the Employer must extend the appraisal period until an observing official has supervised the employee for at least 60 days, per 5 C.F.R. § 430.207. Failure to do so results in"
            " an invalid rating of record, as the rater lacks sufficient direct knowledge to fairly evaluate the employee’s performance. Instead of rushing to complete an appraisal without the required"
            " observation period, management should have extended the period as required by regulation. To prevent this from happening again, rating timelines should be tracked, and a flag should be raised"
            " whenever a rater does not meet the 60-day threshold, automatically triggering an appraisal extension until a valid rating can be issued. "
        },
        "Management did not have the minimum 60 calendar days needed to perform an appraisal for an employee.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208, 5 C.F.R. § 430.207 "],
            "argument": "A rating of record cannot be issued unless the employee has been under the supervision of the rating official for at least 60 calendar days. When a rating is issued without meeting this"
            " threshold, it undermines the legitimacy of the performance evaluation, as the rater lacks sufficient observation to make an informed and fair assessment. This premature rating violates both"
            " regulatory guidance and contractual obligations, and can negatively impact employee rights and opportunities. Instead, the Employer should have either extended the appraisal period or reassigned"
            " the rating responsibility to a qualified prior supervisor. To correct this, management should conduct a review of all issued ratings to confirm supervisory timeframes and re-issue any ratings that"
            " fail the 60-day requirement. Training should also be provided to all rating officials on appraisal timing compliance."
        },
        "Failure to use the most recent rating of record during extension.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "When an employee’s appraisal period is extended due to a lack of a qualified rater, the most recent valid rating of record must remain in effect for all personnel decisions until a new"
            " one is issued. Failing to apply the prior rating results in unjust gaps in evaluation history, potentially affecting pay increases, promotions, and awards. This misstep can disadvantage employees"
            " who earned a valid rating within the last appraisal cycle. Instead, the prior rating should be retained and used as the basis for performance-related decisions until a compliant rating is issued."
            " To resolve this, the Employer must audit records to identify instances where prior ratings were not used and retroactively apply the appropriate ratings where necessary. "
        },
        "Improper change to the established annual rating period. ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Annual appraisal periods are contractually defined and must not be altered without proper notice, agreement, and adherence to established procedures under Article 12. Arbitrarily changing"
            " the rating period undermines the fairness and consistency of the performance management system and can result in ratings being based on incomplete or inconsistent data. Instead, the established"
            " cycle must be maintained unless officially bargained and documented, with all stakeholders—including the Union—properly notified. To fix this, management should review any deviations from standard"
            " appraisal timelines and reissue any affected appraisals using the correct period. Guidance should be reinforced at the local and national level to ensure adherence to the officially bargained rating"
            " cycle. "
        },
        "Improper impact on within-grade increases, promotions, or other actions due to delay or extension. ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Delays or extensions in issuing performance appraisals must not be used to withhold or defer personnel actions such as within-grade increases (WGIs), promotions, or awards unless there"
            " is valid, documented justification. Doing so is both procedurally improper and potentially violates merit system principles and employee rights. The most recent valid rating must be used as the"
            " basis for eligibility determinations until a new rating of record is available. To avoid future violations, management should track appraisal delays and implement safeguards to ensure that"
            " employees are not denied timely personnel actions due to administrative errors. In cases where an action was improperly withheld, corrective actions including back pay or retroactive promotion"
            " should be taken."
        },
        "Use of an expired or non-contractually compliant rating for merit promotion. ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Using an expired rating (older than four years) or a rating issued outside of contractual or regulatory standards (e.g., issued without 60 days of observation) violates both Article 12"
            " and Article 13. Such ratings lack validity and should not influence merit promotion or other employment decisions. Doing so introduces bias, unreliability, and opens the Employer to grievances or"
            " equal opportunity complaints. Instead, only ratings that meet all criteria—including timing, observation requirements, and documentation—should be accepted in promotion packages. To prevent"
            " recurrence, selecting officials must receive updated guidance on what constitutes an acceptable rating, and any use of invalid ratings must be rectified through re-competition or other corrective"
            " actions."
        },
        "Inconsistent application of ratings for other personnel actions (e.g., RIFs). ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "Ratings of record must be consistently and fairly applied across all personnel actions, including reductions in force (RIFs), reassignments, and eligibility decisions."
            " Inconsistency—such as using an outdated or unverified rating for one employee but not another—violates merit principles and the National Agreement. This creates inequity and exposes the Employer"
            " to grievances, arbitration, or even litigation. Instead, the Employer must develop a standardized process to ensure consistent application and verification of ratings for all actions. Any"
            " inconsistencies identified must be corrected by reapplying decisions with verified, contractually compliant ratings of record and issuing remedies where harm occurred. Going forward,"
            " decision-makers should be required to document their sources and justification for any rating used in such actions. "
        },
        "Failure to provide a merit promotion appraisal upon request when no prior rating exists.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208 "],
            "argument": "When an employee has no prior rating of record and requests an appraisal for a merit promotion, management is obligated to provide one based on available performance observations."
            " Failure to do so results in the unjust exclusion of the employee from fair promotional opportunities, disadvantaging them without cause. This action undermines the merit-based principles and"
            " transparency expected in promotion decisions. Instead, management should have provided an interim or summary appraisal reflecting the employee’s observed performance. Moving forward, supervisors"
            " must respond promptly to such requests and provide a fair, timely assessment when no existing rating is available. Clear internal procedures should be established to ensure such requests are never"
            " overlooked. "
        },
        "Refusal to issue Form 6850-BU after 60 days on performance plan. ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "When an employee has served on a performance plan for at least 60 days, they are eligible for a formal appraisal using the appropriate form. Refusing to issue the form denies the"
            " employee documentation of their performance and delays critical personnel actions, such as promotions or awards. The appraisal process is intended to recognize work and provide feedback—denying"
            " it weakens employee trust and accountability. Instead, the form should be completed and shared with the employee once the 60-day threshold is reached. To correct this, management should review"
            " any pending cases where forms were withheld and issue them accordingly. Supervisors must be trained to monitor performance plan timelines and fulfill their documentation responsibilities without"
            " delay. "
        },
        "Failure to extend appraisal period for new GS-4 or higher employees who haven’t completed 6 months. ": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "If an employee in a GS-4 or higher position has not completed 6 months on their performance plan by the end of the appraisal cycle, their rating period should be extended to ensure"
            " adequate observation. Failing to do this results in an unfair and potentially invalid appraisal, as insufficient time was provided to evaluate their performance accurately. The employee is then"
            " judged on a limited sample of work that may not reflect their true capabilities. Instead, the appraisal period should have been formally extended to allow for a full 6 months of observation. To"
            " fix this, supervisors must track new hires and reassigned employees to ensure appraisal timelines are adjusted. Reviews should be conducted to identify and correct any early appraisals issued"
            " under incomplete service periods."
        },
        "Issuance of a “Minimally Successful” rating before 6 months of service.": {
            "articles": ["Article 12, Section 4, 5 C.F.R § 430.208"],
            "argument": "A rating of “Minimally Successful” issued before an employee completes 6 months of service lacks sufficient performance data and can unjustly harm their reputation and future"
            " opportunities. This premature assessment does not allow for a fair evaluation of work patterns, adjustment to job expectations, or time to receive necessary feedback. Instead, management should"
            " have either provided coaching or extended the appraisal period to allow the employee to demonstrate improvement. To correct this, the rating should be withdrawn or re-evaluated based on complete"
            " and fair performance data. Supervisors must ensure that negative ratings are never assigned before adequate observation and opportunity for success."
        },
        "Rating is inconsistent with prior feedback": {
            "articles": ["Article 21, Section 4"],
            "argument": "The rating is inconsistent with prior feedback, violating Article 21, Section 4."
        },
        "Rating is inconsistent with peer comparisons": {
            "articles": ["Article 21, Section 5"],
            "argument": "The rating is inconsistent with peer comparisons, violating Article 21, Section 5."
        },
        "Performance elements were not clearly defined": {
            "articles": ["Article 12 Section 3"],
            "argument": "Performance elements were not clearly defined, violating Article 21, Section 2."
        },
        "Employee was not given opportunity to improve": {
            "articles": ["Article 12, Section 7"],
            "argument": "The employee was not given the opportunity to improve, violating Article 12, Section 7."
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
        issue_description = st.text_area("Summary of Grievance", key="issue_description")
        desired_outcome = st.text_area("Requested Resolution", key="desired_outcome")

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

        filing_step = "Step Two - Streamlined Grievance"
        
        # All fields for the cover sheet (in order)
        form_data = {
            "Step": filing_step,
            "Grievant": grievant,
            "Appraisal Year": appraisal_year,
            "Current Rating": rating_received,
            "Prior Year’s Rating": previous_rating,
            "Issue Description": issue_description,
            "Desired Outcome": desired_outcome,
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
                                if isinstance(converted_path, BytesIO):
                                    converted_path.seek(0)
                                    merger.append(converted_path)
                                else:
                                    with open(converted_path, "rb") as f:
                                        merger.append(f)
                except Exception as e:
                    st.warning(f"⚠️ Skipped {filename} due to error: {e}")

        output_name = f"{grievant.replace(' ', '_')}_{appraisal_year}_Annual_Argument.pdf"
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
