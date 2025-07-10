import streamlit as st
import datetime
import holidays
import tempfile
import os
from io import BytesIO
from PyPDF2 import PdfMerger
from util import wrap_text_to_width, draw_wrapped_section, generate_pdf, convert_to_pdf, calculate_fbd, create_cover_sheet, merge_pdfs

def render_awol():
    st.header("AWOL - Annual or Sick Leave Grievance Intake")
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

    case_id = st.text_input("Case Number")
    steward = st.text_input("Steward's Name")
    grievant = st.text_input("Grievant's Name")
    workarea = st.text_input("Work Area/ Operation")
    dept_man = st.text_input("Department Manager")
    flmanager = st.text_input("Frontline Manager")
    position = st.text_input("Title/Position")
    issue_description = st.text_area("Summary of Grievance", key="issue_description")
    desired_outcome = st.text_area("Requested Resolution", key="desired_outcome")

    # Multi-file uploader
    uploaded_files = st.file_uploader(
        "Upload Supporting Documents (PDF, DOCX, TXT, JPG, PNG)",
        type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="file_uploader_multi"
    )

    st.subheader("Alleged Violations:\nAnnual Leave")

    # Define AWOL-related checkbox content
    awol_checkbox_descriptions = {
        "Annual Leave denied but no statement of reasoning provided after requested by the employee.": {
            "articles": ["Article 32 Section 1(A)(1)"],
            "argument": "It is a violation of the negotiated rights under the National Agreement to deny an employee’s request for annual leave without providing a clear and timely explanation"
            " for the denial. The National Agreement outlines that, while management retains the right to approve or disapprove leave, such decisions must not be arbitrary or capricious and must be based on legitimate"
            " operational needs. When a leave request is denied, the employee has the right to understand the basis for that decision. \n\n Failure to provide the reason(s) for denial upon request"
            " undermines transparency and accountability and prevents the employee from exercising their right to challenge the denial through appropriate channels, such as the grievance process. This"
            " lack of justification also hampers the union’s ability to determine whether the denial was consistent with past practices, equitable treatment, and the principles of fair and reasonable"
            " application of leave policies. \n\n In this case, management did not offer a statement of reasons for denying the annual leave, even after being requested to do so. This omission"
            " constitutes a violation of the National Agreement, which implicitly and through past interpretive guidance, expects management to act in good faith and provide supporting rationale for decisions that impact"
            " bargaining unit employees’ rights. \n\n"
        },
        "Issues with utilzing 15-min increments.": {
            "articles": ["Article 32 Section 1(A)(2)"],
            "argument": "It is a violation of an employee’s rights under the National Agreement to restrict or deny the use of earned annual leave in increments other than those expressly outlined in"
            " the contract. The National Agreement clearly provides that employees may request and use annual leave in 15-minute increments, and any attempt by management to enforce a different standard—such as requiring"
            " leave to be taken in larger blocks is inconsistent with the negotiated language. \n\n Employees earn annual leave as a benefit of federal service, and once accrued, they have the right to use"
            " that leave subject to approval consistent with operational needs—not arbitrary restrictions on increment size. Denying or charging leave in increments larger than 15 minutes without a valid"
            " contractual basis violates the principles of fairness, consistency, and negotiated rights. \n\n In this case, management's decision to either refuse an employee’s request for annual leave in"
            " a 15-minute increment or to charge the employee leave in a greater amount than requested exceeds their authority under the National Agreement. Such action not only infringes on the employee’s rights but also"
            " establishes a concerning precedent that undermines contractually guaranteed flexibilities afforded to bargaining unit employees. \n"
        },
        "Use or Lose - Employer provided confirmation in writing to employee of Use or Lose after management canceled requested Use or Lose.": {
            "articles": ["Article 32 Section 1(B)"],
            "argument": "When management cancels previously approved use-or-lose annual leave, they are obligated under the National Agreement and applicable government-wide regulations to provide the"
            " employee with written confirmation of the leave restoration. This requirement ensures that the employee is not unfairly penalized for circumstances beyond their control and preserves their"
            " right to use that leave at a later date without it being forfeited. \n\n Failure by management to issue timely written documentation confirming the restoration of the canceled leave constitutes"
            " a violation of the employee’s rights. The restoration process is not automatic and depends on the existence of a formal record showing that the leave was scheduled in advance, was canceled due"
            " to agency necessity, and is now authorized for restoration. Without this written confirmation, the employee may lose valuable earned leave, despite having followed all procedural requirements."
            "\n\n In this case, management canceled the employee’s scheduled use-or-lose leave but failed to provide written notification or documentation of restoration. This oversight not only violates"
            " procedural obligations but also deprives the employee of their ability to recover and use the leave in the future. Such an action undermines the intent of both the National Agreement and Office"
            " of Personnel Management (OPM) regulations, which are designed to protect employees from unjust forfeiture of their earned benefits. \n"
        },
        "Conflict in requests but EOD order was not utilized.": {
            "articles": ["Article 32 Section 1(C)"],
            "argument": "Management violated the National Agreement by failing to adhere to the established Enter-On-Duty (EOD) date order when approving and denying annual leave requests. The National Agreement provides"
            " that when two or more employees within a work unit request overlapping periods of leave and operational needs prevent approving all requests, priority must be given based on the employees’ EOD"
            " dates, with the employee having the earlier EOD date receiving preference. \n\n In this case, the employee who was denied leave had an earlier EOD date than another employee whose overlapping"
            " leave request was approved. By approving the more junior employee’s request over that of the more senior employee, management failed to apply the required order of consideration, thereby violating"
            " the negotiated leave approval process outlined in the National Agreement. This not only undermines the fairness and consistency of leave administration but also diminishes employee trust in the equitable"
            " application of contract provisions. \n"
        },
        "Annual leave request not timely responded to by management.": {
            "articles": ["Article 32 Section 1(D)"],
            "argument": "It is a violation of the employee’s rights under the National Agreement for management to take an excessive or unreasonable amount of time to respond to a leave request."
            " The National Agreement obligates management to act promptly and reasonably when reviewing and responding to such requests, recognizing that timely responses are essential for employees to plan their personal and"
            " family obligations effectively. \n\n Delays in leave approval or denial decisions can create uncertainty, cause undue stress, and disrupt personal responsibilities, ultimately undermining morale"
            " and the employee’s ability to maintain a healthy work-life balance—an outcome the National Agreement expressly seeks to prevent. The intent of the negotiated provisions surrounding leave administration is to"
            " foster fairness, consistency, and respect for employees’ personal time, which cannot occur when decisions are left pending for prolonged periods. \n\n In this case, management failed to issue"
            " a timely response to the leave request, thereby denying the employee the opportunity to make necessary arrangements. Such inaction is inconsistent with the principles laid out in the National Agreement and"
            " should be addressed to ensure that employees’ rights and well-being are protected moving forward.\n"
        },
        "Employee's leave request was affected by another employee requesting time.": {
            "articles": ["Article 32 Section 2"],
            "argument": "It is a violation of the employee’s rights under the National Agreement for management to alter, deny, or adjust one employee’s leave request based solely on the leave request of"
            " another employee. The National Agreement provides that all leave requests must be considered individually and fairly, and that decisions must be based on legitimate operational needs—not on"
            " favoritism, convenience, or preference tied to another employee’s request. \n\n Allowing one employee’s leave request to directly impact the approval of another’s—particularly when both"
            " employees are otherwise eligible and have followed the correct procedures—undermines the principles of equitable treatment and transparency laid out in the contract. Each employee’s request"
            " should be evaluated on its own merits, and in cases of scheduling conflicts, contractual provisions as outlined in the National Agreement, must be followed. \n\n In this case, management"
            " improperly adjusted or denied the employee’s leave request in response to another employee’s request, without applying the appropriate negotiated criteria. This action represents a failure to"
            " administer leave fairly and consistently and constitutes a breach of the employee’s contractual rights. \n"
        },
        "Seasonal Employees - Placed in non-pay status for 10 days or less and was denied us of annual leave.": {
            "articles": ["Article 32 Section 3(A)"],
            "argument": "Management violated the National Agreement by inappropriately denying a seasonal employee the use of their earned annual leave while in a non-pay status for fewer than 10 workdays."
            " The National Agreement does not contain any provision that permits the blanket denial of annual leave for seasonal employees solely based on a short-term non-pay status. Seasonal employees"
            " are entitled to the same leave rights as other bargaining unit employees, and earned leave cannot be withheld without a valid and contractually supported reason. \n\n By refusing to allow the"
            " employee to use their annual leave during this brief non-pay period, management failed to uphold the contractual standards for equitable and consistent leave administration. This action denied"
            " the employee access to a benefit they had earned and were entitled to use, constituting a direct violation of the National Agreement. Such conduct not only disregards the negotiated rights of"
            " seasonal employees, but also sets a harmful precedent that undermines the fair treatment of all employees under the agreement. \n"
        },
        "Seasonal Employees - Requested leave within the last 10 workdays of any fiscal year was denied based on anything except staffing and budgetary restrictions.": {
            "articles": ["Article 32 Section 3(B)"],
            "argument": "Management violated the National Agreement by denying the employee’s request for annual leave during the final 10 workdays of the fiscal year for reasons unrelated to staffing or"
            " budgetary restrictions. The National Agreement provides that while management may deny annual leave during this specific time period, such denials must be based solely on legitimate staffing"
            " needs or financial constraints. Any other reason for denial during this timeframe is not contractually supported and constitutes a violation of the employee’s rights. \n\n In this case,"
            " management denied the leave request without citing staffing shortages or budgetary limitations, thereby exceeding the authority granted under the National Agreement. This action improperly"
            " restricted the employee’s ability to use their earned leave and disregarded the limited and specific circumstances under which such a denial is permitted. By doing so, management not only"
            " failed to follow the negotiated process but also undermined the principle of fair and transparent leave administration guaranteed to all bargaining unit employees.  \n"
        },
        "Seasonal Employees - Seasonal Employees leave requests are not being handled like a regular employees leave request would be.": {
            "articles": ["Article 32 Section 3(C)"],
            "argument": "Management violated the National Agreement by failing to treat a seasonal employee’s annual leave request with the same consideration afforded to non-probationary employees. The"
            " National Agreement explicitly requires that seasonal employees be granted the same rights and benefits related to leave as any other bargaining unit employee, including during peak season"
            " operations. \n\n By denying or deprioritizing the seasonal employee’s leave request solely based on their employment category, management disregarded the employee’s earned entitlements and"
            " engaged in discriminatory leave administration. The National Agreement does not permit management to impose additional restrictions on seasonal employees beyond what is applied to permanent"
            " staff. All employees, regardless of seasonal status, have the right to fair, equitable, and contractually consistent treatment when requesting annual leave. \n\n In this case, management’s"
            " decision to treat the seasonal employee’s request differently violated those protections and reflects an improper and unequal application of the negotiated agreement. \n"
        },
        "The employee requested annual leave in advance for a religious holiday and it was not timely handled.": {
            "articles": ["Article 32 Section 4"],
            "argument": "Management violated the National Agreement by failing to make every reasonable effort to approve the employee’s request for annual leave to observe a religious holiday. The National"
            " Agreement explicitly requires that management give full and fair consideration to leave requests for religious observances and make every reasonable effort to accommodate such requests, especially"
            " when operational needs allow for it. \n\n In this case, there were no demonstrated issues with workload or staffing that would have justified denying the leave. Despite this, management refused"
            " to approve the request, disregarding the employee’s religious rights and the contractual obligation to support religious accommodation whenever feasible. This constitutes a direct violation of the"
            " employee’s rights under the National Agreement and reflects a failure to uphold the Agency’s commitment to respecting diversity, inclusion, and equal treatment in the workplace. \n"
        },
        "An employee was denied the opportunity to utilize annual leave or LWOP for a death in the immediate family.": {
            "articles": ["Article 32 Section 5"],
            "argument": "Management violated the National Agreement by failing to approve annual leave or grant Leave Without Pay (LWOP) for the employee following the death of an immediate family member."
            " The National Agreement provides that, upon request, an employee may be granted up to five workdays of annual leave or LWOP in connection with the death of an immediate family member. This"
            " provision exists to ensure employees are given the time and space necessary to grieve and manage personal and family responsibilities during such a difficult time. \n\n In this case, the"
            " employee properly submitted a request for leave due to a qualifying family death, yet management failed to approve the leave or offer LWOP as an alternative. This refusal is a clear violation"
            " of the employee’s contractual rights and shows a lack of compassion and compliance with the obligations set forth in the National Agreement. Such actions undermine employee well-being and"
            " morale, and directly contradict the standards of humane and respectful treatment negotiated in the agreement.\n"
        },
        "Employee was denied advanced annual and met the following conditions:\n"
        "  • Has less than 40 hours of advanced annual balance.\n"
        "  • Completed 1st year of probationary time.\n"
        "  • Been in current appointment for more than 90 days.\n"
        "  • Is eligible to earn annual leave.\n"
        "  • Did not request more advanced leave than could be earned during the remainder of the leave year.\n"
        "  • Is expected to return to work after having used the leave.": {
            "articles": ["Article 32 Section 6(A)"],
            "argument": "Management violated the National Agreement by denying the grievant’s request for advanced annual leave despite the employee meeting all qualifications required under the contract."
            " The National Agreement explicitly states that advanced annual leave will be granted when an employee satisfies the outlined criteria, including a demonstrated need, sufficient time remaining"
            " in the leave year to earn the leave back, and no history of misuse or abuse. \n\n In this case, the grievant met all of those requirements, yet management failed to approve the request."
            " This constitutes a direct violation of the employee’s rights under the National Agreement. The denial was not based on any contractually permitted reason and reflects a failure to follow the"
            " mandatory provisions governing advanced leave approval. By refusing the request without justification, management disregarded the negotiated protections in place to support employees facing"
            " temporary hardships and disrupted the fair and equitable administration of leave. \n"
        },
        "Denied additional advanced annual leave over the 40 hours limitation due to:\n"
        "  • A serious health condition.\n"
        "  • Or to care for a family member.": {
            "articles": ["Article 32 Section 6(B); Exhibit 33-1"],
            "argument": "Management violated the National Agreement by denying the employee’s request for more than 40 hours of advanced annual leave, despite the fact that the request was made due to a"
            " serious health condition affecting the employee or a qualifying family member. The National Agreement provides a specific exception to the standard 40-hour cap on advanced annual leave in cases"
            " involving serious health conditions. When such conditions exist, and the employee meets the other qualifying criteria, management is obligated to grant the leave in accordance with the"
            " negotiated terms. \n\n In this case, the employee's situation clearly met the exception outlined in the National Agreement, yet management failed to approve the request or provide valid"
            " justification for the denial. This constitutes a direct violation of the employee’s rights and reflects a failure to uphold the agreed-upon provisions designed to support employees during times"
            " of medical hardship. By disregarding this exception, management not only breached the contract but also failed to demonstrate the compassion and flexibility that the provision was specifically"
            " intended to provide. \n"
        },
        "The Agency failed to allow an employee to repay the balance due via earned annual leave or through a cash payment.": {
            "articles": ["Article 32 Section 6(C)"],
            "argument": "Management violated the National Agreement by failing to allow the grievant to repay advanced annual leave using one of the repayment methods explicitly permitted under the contract."
            " The National Agreement clearly outlines that an employee who has received advanced annual leave may repay the borrowed hours either through the accrual of future annual leave or by making a cash"
            " payment. These are the only two repayment methods authorized under the agreement. \n\n In this case, management failed to offer or permit either of these contractually required repayment options,"
            " thereby imposing an unauthorized repayment method or unjustly penalizing the employee. This action constitutes a direct violation of the employee’s rights under the National Agreement. By not"
            " adhering to the agreed-upon procedures, management disregarded the negotiated safeguards that protect employees from arbitrary or inconsistent debt collection practices related to advanced leave. \n"
        },
        "The employer did not make every reasonable effort to approve advanced annual leave consistent with workload and staffing needs.": {
            "articles": ["Article 32 Section 6(D)"],
            "argument": "Management violated the National Agreement by failing to make every reasonable effort to grant the employee’s request for advanced annual leave, despite the absence of any legitimate"
            " workload or staffing barriers that would have prevented approval. The National Agreement requires that management consider such requests in good faith and approve them whenever operational needs"
            " allow, emphasizing a balanced approach that supports both mission requirements and employee well-being. \n\n In this case, management did not evaluate the request in accordance with those"
            " standards and failed to justify the denial based on workload or staffing constraints. This failure to act in good faith directly contradicts the intent of the National Agreement and resulted in"
            " unnecessary harm to the employee. By ignoring the negotiated obligation to consider advanced leave requests thoughtfully and reasonably, management not only created unjust hardship but also"
            " breached the employee’s contractual rights. \n"
        },
        "The employer granted advanced annual leave for one employee and denied another employee the right to use annual leave.": {
            "articles": ["Article 32 Section 6(D)"],
            "argument": "Management violated the National Agreement by approving advanced annual leave for one employee while improperly denying a timely and qualifying request for annual leave from another."
            " The National Agreement establishes that advanced annual leave should only be approved after all timely and qualifying requests for regular earned annual leave have been fully considered and"
            " addressed. This ensures a fair and orderly process that prioritizes the use of accrued leave before resorting to leave that has not yet been earned. \n\n In this case, management disregarded"
            " this contractual requirement by granting advanced leave without first honoring a valid request from another employee for their accrued annual leave. This action not only disrupted the integrity"
            " of the leave approval process but also resulted in the unjust denial of earned benefits to the affected employee. By failing to follow the correct order of consideration, management breached the"
            " provisions of the National Agreement and violated the employee’s rights to equitable leave treatment. \n"
        },
        "The employer failed to notify an employee of an AWOL charge in writing, no later than:"
        "  • The end of a pay period. \n"
        "  • Or 2 workdays from the end of the pay period. - If the AWOL charge occured during the last 2 days of the pay period (Friday or Saturday.)": {
            "articles": ["Article 32 Section 9"],
            "argument": "Management violated the National Agreement by failing to properly and timely notify the employee of the AWOL charge. The National Agreement clearly requires that employees be notified"
            " of any AWOL charge no later than the end of the pay period in which the absence occurred. The only exception to this requirement is if the AWOL in question occurred on the last two days of the"
            " pay period—specifically, on the Friday or Saturday of Week Two. In such cases, management is granted an additional two workdays following the end of the pay period to issue proper notification."
            "\n\n In this instance, the absence did not fall within the exception window, and management failed to provide the required notice by the contractual deadline. This failure not only constitutes a"
            " clear violation of the employee’s rights under the National Agreement but also caused unjust and avoidable harm to the grievant. Timely notification is critical to ensuring due process, allowing"
            " employees the opportunity to respond, correct any issues, or provide documentation in their defense. By disregarding this obligation, management denied the employee that opportunity and undermined"
            " the procedural fairness guaranteed by the Agreement. \n"
        }
    }
    sick_awol_checkbox_descriptions = {
        "The employer failed to allow the employee to accumulate leave according to statutes and regulations.": {
            "articles": ["Article 34 Section 1"],
            "argument": "Management violated the employee’s rights by failing to allow the accrual of annual leave in accordance with federal laws and regulations governing leave entitlements for federal"
            " employees. Under 5 U.S.C. § 6303 and 5 C.F.R. Part 630, eligible federal employees are entitled to accrue annual leave based on their length of service, with accrual rates clearly defined by"
            " statute. These laws are not discretionary and must be applied consistently and uniformly to all qualifying employees. \n\n By failing to credit the employee with the appropriate amount of annual"
            " leave, management disregarded these governing statutes and regulations. This denial not only violates federal law but also breaches the terms of the National Agreement, which incorporates adherence"
            " to applicable leave laws as a condition of employment. Employees have a right to earn and utilize annual leave as prescribed, and any interference with that process constitutes a violation of"
            " both legal and contractual obligations. \n"
        },
        "The employer failed to allow the utilization of sick leave in 15-min increments.": {
            "articles": ["Article 34 Section 1"],
            "argument": "Management violated the National Agreement and applicable federal regulations by failing to allow the grievant to use sick leave in 15-minute increments. The National Agreement"
            " explicitly states that sick leave may be granted in increments of no less than 15 minutes, aligning with OPM regulations under 5 C.F.R. § 630.206, which provide that leave (including sick leave)"
            " is to be charged in minimum units of 15 minutes unless otherwise negotiated. \n\n In this case, management either denied the use of sick leave or required it to be used in larger increments"
            " than permitted, thereby restricting the employee’s access to earned benefits in a manner inconsistent with both contractual and regulatory guidance. This is a clear violation of the grievant’s"
            " rights. The 15-minute increment rule exists to provide flexibility and fairness in the administration of leave and must be honored uniformly. By deviating from this requirement, management"
            " imposed an arbitrary barrier on the use of sick leave, resulting in an improper and unjust denial of the employee’s entitlements.  \n"
        },
        "Approval of sick leave did not comply with Exhibit 34-1 (NA).": {
            "articles": ["Article 34 Section 2(A); Exhibit 34-1"],
            "argument": "Management violated the National Agreement by failing to follow the clearly defined leave approval process and guidelines outlined in Article 34 and Exhibit 34-1 of the National"
            " Agreement. These sections establish the procedures, timelines, and standards that must be followed when evaluating and approving leave requests. The negotiated provisions are binding and were"
            " designed to ensure consistency, fairness, and transparency in leave administration across the bargaining unit. \n\n By disregarding the process laid out in Article 34 and its associated exhibit,"
            " management failed to meet its contractual obligations and deprived the employee of protections guaranteed under the Agreement. This failure to adhere to the established guidance is not a matter"
            " of discretion—it is a clear violation of the employee’s rights. Proper leave administration is a critical part of maintaining trust and accountability in the workplace, and any deviation from"
            " the agreed-upon procedures constitutes a breach of the National Agreement. \n"
        },
        "Denied sick leave because the employee requested sick leave outside the 2-hour limit from their normal time to report but the degree of the illness prevented the employee"
        " from meeting this requirement.": {
            "articles": ["Article 34 Section 2(B)"],
            "argument": "Management violated the National Agreement by failing to appropriately consider the grievant’s inability to provide notice of their sick leave request within the standard two-hour"
            " timeframe due to the severity of their illness. As outlined in Article 34 of the National Agreement, employees are required to notify management within two hours of their normal reporting time"
            " when requesting sick leave. However, the Agreement explicitly recognizes that this requirement may be waived when the degree of illness makes timely notification impractical or impossible. \n\n"
            " In this case, the employee’s condition clearly prevented them from complying with the two-hour notification window. Management’s refusal to acknowledge this exception and subsequent"
            " disciplinary or leave-related action taken as a result is a direct violation of the employee’s contractual rights. The National Agreement was deliberately crafted to account for real-life medical"
            " situations where immediate communication may not be feasible, and management’s failure to apply this clause fairly and with compassion disregards both the letter and spirit of the Agreement. \n"
        },
        "Denied sick leave despite the employee following the sick leave procedure:\n"
        "  • Current telephone number was included via email or voicemail.\n"
        "  • Not under a sick leave restriction.": {
            "articles": ["Article 34 Section 2(B)"],
            "argument": "Management violated the National Agreement by denying the grievant’s sick leave request on the grounds of procedural noncompliance, even though the employee fully adhered to the"
            " procedures outlined in Article 34 of the National Agreement. The Agreement specifies that when requesting sick leave, an employee must provide appropriate notification—such as a phone call,"
            " voicemail, or email—and, where possible, include a return phone number for follow-up communication. \n\n In this case, the grievant complied with these requirements by notifying management in"
            " a timely manner and leaving a contact number as required. Despite this, management improperly denied the leave request, claiming that the employee failed to follow the procedure. This denial was"
            " not supported by the facts or the contractual language, and therefore constitutes a clear violation of the employee’s rights under the National Agreement. The purpose of these procedures is"
            " to ensure reliable communication—not to create a pretext for unjust leave denials. By ignoring the employee’s compliance, management acted in bad faith and failed to uphold the obligations agreed"
            " to in the contract. \n"
        },
        "The employer did not take into consideration the self-certification from an employee for leave of less than 3 consecutive workdays.": {
            "articles": ["Article 34 Section 3(A)"],
            "argument": "Management violated the National Agreement by refusing to accept the grievant’s self-certification for sick leave covering an absence of three consecutive workdays or less, despite"
            " the fact that the grievant was not under a sick leave restriction. Article 34 of the National Agreement clearly states that for absences of three consecutive workdays or fewer, employees may"
            " self-certify the reason for their use of sick leave, unless they have been officially placed on a sick leave restriction. \n\n In this case, the grievant complied fully with the"
            " self-certification process as outlined in the National Agreement and was not subject to any restriction that would warrant requiring medical documentation. Management’s refusal to honor the"
            " employee’s self-certification is a direct violation of the contractual provisions negotiated to ensure fair and consistent treatment of all employees. Furthermore, this action also violates"
            " government-wide rules under 5 C.F.R. § 630, which reinforce the right of employees to self-certify short-term absences unless otherwise notified in writing. \n\n By disregarding these clear"
            " provisions, management unjustly denied the employee’s earned benefit, undermined the integrity of the negotiated agreement, and imposed arbitrary barriers to leave access in violation of both"
            " contract and federal regulation.  \n"
        },
        "The employer required medical documentation for less than 3 consecutive workdays.": {
            "articles": ["Article 34 Section 3(B)"],
            "argument": "Management violated the National Agreement by improperly requiring the grievant to submit additional medical documentation for a sick leave absence of three consecutive workdays"
            " or less, despite the fact that the grievant was not under a sick leave restriction. According to Article 34 of the National Agreement, employees are permitted to self-certify the reason for"
            " their use of sick leave for absences of three consecutive workdays or fewer, unless they have been formally placed on a sick leave restriction through written notification. \n\n In this case,"
            " the grievant complied with the self-certification procedures established by the Agreement. However, management demanded unnecessary documentation, placing an unfair burden on the employee and"
            " exceeding the authority granted by the National Agreement. This demand contradicts not only the terms of the contract but also undermines the protections in place to ensure employee trust and"
            " flexibility in managing short-term medical needs. \n\n By requiring documentation without contractual justification, management disregarded the rights afforded to the employee, creating undue"
            " stress and violating both the letter and spirit of the Agreement. This constitutes a clear breach of the employee’s negotiated rights. \n"
        },
        "Denied based on issues with the medical documentation. Must include: \n"
        "  • Statement employee is under the care of a health professional.\n"
        "  • Statement that the employee was incapacitated.\n"
        "      * DOES NOT HAVE TO USE THE WORD ""INCAPACITATED"" \n"
        "  • Include the duration of incapacitation. \n"
        "  • Sign or stamp of signature by Health Care Provider.": {
            "articles": ["Article 34 Section 3(C)"],
            "argument": "Management violated the National Agreement by imposing documentation requirements for a medical certificate that exceeded what is contractually allowed. Article 34 of the National"
            " Agreement outlines the specific elements that a medical certificate must include when required: \n\n A statement that the employee is under the care of a health care provider, \n"
            " Confirmation that the employee was incapacitated for duty, \n The expected duration of the incapacitation, and \n A signature or stamped signature from the health care provider. \n\n"
            ' While the term "incapacitated” is used in the Agreement to describe the employee’s inability to perform their duties, the use of the specific word “incapacitated” within the written medical'
            "certificate is not required. The intent of the provision is to ensure that a health care provider affirms the employee’s inability to work—not to require rigid phrasing or unnecessary legalese."
            ' Therefore, management’s insistence on the literal inclusion of the word “incapacitated” or any other language not explicitly required by the National Agreement constitutes an unauthorized'
            " change to negotiated procedures. \n\n By requiring documentation beyond what is prescribed, management not only violated the terms of the Agreement but also abused its authority by attempting"
            " to impose higher standards than those mutually agreed upon. This overreach infringes on the rights of the employee and undermines the protections negotiated by NTEU to ensure consistency,"
            " clarity, and fairness in leave documentation requirements. \n"
        },
        "Denied leave because employee did not timely provide documentation within 15 days after the date requested but employee did not provide documentation within this time frame.": {
            "articles": ["Article 34 Section 3(D)"],
            "argument": "Management violated the National Agreement by denying the grievant’s sick leave request solely because the supporting documentation was not submitted immediately, despite the fact"
            " that the employee was still within the allowable timeframe to provide it. According to the National Agreement, employees are granted up to 15 calendar days from the date management requests"
            " documentation to submit a medical certificate or other supporting records. This provision ensures that employees have a fair and reasonable amount of time to obtain necessary paperwork, especially"
            " when dealing with health care providers and recovery from illness. \n\n In this case, the grievant had not exceeded the 15-day timeframe, meaning management’s denial was premature and unjustified."
            " Requiring documentation earlier than the contractually agreed period—or penalizing an employee for not submitting it before that period ends—is a direct violation of the employee’s contractual"
            " rights. It disregards the negotiated protections in the National Agreement and imposes arbitrary burdens not supported by law or agreement. \n\n By denying sick leave under these conditions,"
            " management acted outside the bounds of its authority and failed to comply with the processes and timelines specifically designed to protect employees during periods of illness. \n"
        },
        "Circumstances of the requested leave prevented the employee from meeting the 15-day deadline and the Agency did not allow for the employee , up to 30 days, after"
        " the requested leave due to circumstances.": {
            "articles": ["Article 34 Section 3(D)"],
            "argument": "Management violated the National Agreement by requiring the grievant to submit medical certification earlier than what is contractually permitted. Article 34 of the National Agreement"
            " allows an employee up to 30 calendar days from the date of management’s request to provide medical documentation, if it is not practicable to obtain it sooner. This provision accounts for"
            " situations where obtaining records from health care providers may take time due to scheduling, administrative delays, or the employee’s medical condition. \n\n In this case, the grievant"
            " communicated that it was not practicable to obtain the certification immediately, and therefore should have been granted the full 30-day period allowed under the National Agreement. Management’s"
            " insistence on earlier submission—prior to the expiration of the permitted timeframe—constitutes a clear violation of the employee’s contractual rights and demonstrates a failure to adhere to"
            " agreed-upon procedures. \n\n By imposing an unreasonable and unauthorized deadline, management ignored the flexibility negotiated into the Agreement, creating undue pressure on the employee"
            " and undermining the integrity of the contractual protections in place.  \n"
        },
        "Employer required an employee to provide medical documentation because of:\n"
        "  • A specific work day or work time. \n"
        "  • High volume day \n"
        "  • Black out day \n"
        "  • Critical day": {
            "articles": ["Article 34 Section 3(E)"],
            "argument": 'Management violated the National Agreement by requiring medical documentation solely because the employee’s absence fell on a specific workday deemed by management to be a “critical,”'
            ' “blackout,” or “high volume” day. Article 34, Section 6 of the National Agreement explicitly prohibits management from requiring a medical certificate based solely on the day or time of the absence.'
            " The Agreement was intentionally written this way to prevent arbitrary or retaliatory enforcement of sick leave documentation policies and to preserve fair and consistent treatment for all"
            " employees. \n\n In this case, the grievant’s absence occurred during one of these so-called critical or high-demand periods, and management used that as the only basis to request a medical"
            " certificate. This action directly contradicts the language of the National Agreement and reflects an improper application of authority. Furthermore, when the grievant did not provide documentation"
            "that was never rightfully required, management proceeded to deny the sick leave, compounding the violation. \n\n By disregarding the clear contractual language and basing its decision on timing rather"
            " than legitimate justification—such as a pattern of abuse or a formal sick leave restriction—management violated the employee’s rights and failed to comply with the negotiated procedures under the"
            " National Agreement. \n"
        },
        "The employer placed the employee on a sick leave restriction but failed to provide oral counsel to the employer prior to implementation to allow the employee an opportunity to not"
        " be placed on one.": {
            "articles": ["Article 34 Section 4(A)(1)"],
            "argument": "Management violated the National Agreement by issuing a sick leave restriction to the grievant without first providing an oral counseling, as required by the negotiated procedures."
            " The National Agreement clearly outlines that an employee must receive an oral counseling before any formal sick leave restriction is imposed. This step is critical because it gives the employee"
            " a fair opportunity to understand management's concerns and correct any perceived misuse or attendance issues before being subjected to disciplinary-like restrictions. \n\n In this case, management"
            " failed to provide the required oral counseling and moved directly to a restriction, thereby denying the employee the chance to respond, explain, or adjust their leave usage. This bypassing of due"
            " process is a direct violation of the grievant’s rights under the National Agreement and undermines the good faith obligations that both parties are expected to uphold. \n\n By skipping the"
            " required counseling step, management acted outside the bounds of the contract and imposed a restriction prematurely and improperly, making the action both procedurally and contractually invalid. \n"
        },
        "Employee has been placed on a sick leave restriction that has exceeded the maximum limitation of allowed time for a sick leave restriction.": {
            "articles": ["Article 34 Section 4(A)(3)"],
            "argument": "Management violated the National Agreement by placing the grievant under a sick leave restriction for a period that exceeded the maximum allowed duration. The National Agreement"
            " clearly establishes that a sick leave restriction may be imposed for a period of no more than six months at a time. This limit ensures that restrictions are reviewed periodically and remain"
            " justified based on current circumstances, rather than being imposed indefinitely without reevaluation. \n\n In this case, the grievant remained under a sick leave restriction beyond the six-month"
            " limit, without any formal reassessment, reevaluation, or reissuance as required by the Agreement. This failure to adhere to the contractual time limitation constitutes a clear violation of the"
            " employee’s rights and bypasses the safeguards intended to prevent abuse of authority and protect employees from ongoing, unjustified oversight. \n\n By keeping the restriction in place beyond"
            " the authorized period, management failed to follow the negotiated procedures and denied the employee fair treatment under the terms of the National Agreement. \n"
        },
        "The employee was placed on a sick leave restriction that utilized the employee's usage of approved annual leave and/or leave under FMLA as reasoning rather than absences due to illnesses.": {
            "articles": ["Article 34 Section 4(A)(4)"],
            "argument": "Management violated the National Agreement by considering leave types outside of sick leave—such as annual leave and FMLA leave—when determining whether to place the grievant under a"
            " sick leave restriction. The National Agreement is clear that sick leave restrictions may only be based on the employee’s use and patterns of sick leave, not on other categories of approved leave."
            "\n\n Annual leave is earned and used at the discretion of the employee with supervisor approval, and FMLA leave is a federally protected entitlement under law. Including either of these leave types"
            " as justification for a sick leave restriction not only violates the provisions of the National Agreement but also misrepresents the employee’s actual use of sick leave, resulting in an unfair and"
            " inaccurate evaluation of their attendance. \n\n By factoring in leave categories that should have no bearing on a sick leave determination, management overstepped its authority, ignored"
            " contractual protections, and unlawfully subjected the employee to an unjustified restriction. This is a direct violation of the grievant’s rights as outlined in the National Agreement and"
            " undermines the integrity of the procedures intended to ensure fair treatment.  \n"
        },
        "Employee was denied the usage of annual leave or sick leave based on a sick leave restriction.": {
            "articles": ["Article 34 Section 4(A)(4)"],
            "argument": "Management violated the National Agreement by using a sick leave restriction as grounds to deny the grievant’s request for annual leave or FMLA leave. The National Agreement is clear"
            " that a sick leave restriction only applies to the use of sick leave and does not limit or restrict an employee’s access to other types of leave, such as earned annual leave or leave protected"
            " under the Family and Medical Leave Act (FMLA). \n\n Annual leave is a benefit earned by the employee and must be granted in accordance with the procedures and limitations outlined in the"
            " National Agreement. FMLA leave, governed by federal law, provides employees the right to take leave for qualifying medical or family-related reasons, regardless of any internal leave restriction."
            " Attempting to apply a sick leave restriction as a blanket limitation on other categories of leave constitutes a misuse of managerial authority and a clear breach of the negotiated agreement."
            " \n\n By denying the grievant access to leave they were entitled to based on an unrelated restriction, management violated the employee’s rights, failed to comply with the National Agreement,"
            " and potentially ran afoul of FMLA protections as well. This action is contractually invalid and procedurally unjust.  \n"
        },
        "Employee was forced to provide medical documentation for being released from duty due to illness and did not have a sick leave restriction in place.": {
            "articles": ["Article 34 Section 4(B)"],
            "argument": "Management violated the National Agreement by requesting additional medical documentation from the grievant, who left work early due to illness but was not under a sick leave"
            " restriction. The National Agreement clearly states that for absences of three consecutive workdays or less, an employee’s self-certification is sufficient to support the approval of sick"
            " leave—unless the employee is on a current sick leave restriction. This protection applies equally to partial-day absences, including when an employee departs early from their scheduled tour"
            " of duty. \n\n In this case, the grievant provided a valid self-certification for the partial day of sick leave, which should have been accepted as adequate and contractually sufficient evidence."
            " Management’s decision to demand additional documentation—despite the absence being under the threshold and the employee not being under restriction—was arbitrary, unnecessary, and a direct"
            " violation of the rights guaranteed under the National Agreement. \n\n By ignoring the agreed-upon procedures and imposing requirements beyond those allowed by the contract, management acted"
            " improperly and failed to honor the employee's negotiated protections. \n"
        },
        "Employee has provided to the Agency proof of a chronic condition, is not on a sick leave restriction, and is still being required to furnish medical documentation for the time off for"
        " the chronic condition. \n"
        "  • A chronic condition does not necessarily mean that it requires medical treatment.": {
            "articles": ["Article 34 Section 4(C)"],
            "argument": "Management violated the National Agreement by repeatedly requiring the grievant to furnish medical documentation for absences that were related to a known chronic medical condition,"
            " despite the employee not being under a sick leave restriction. The National Agreement clearly states that when an employee has a chronic condition that necessitates recurring absences, and there"
            " is no active sick leave restriction in place, management shall not require continual medical certification for each occurrence. \n\n The purpose of this provision is to protect employees who are"
            " managing legitimate, ongoing health issues from unnecessary and burdensome documentation requests. In this case, the grievant had already established the existence of a chronic condition with"
            " appropriate documentation, fulfilling their obligation under the National Agreement. By continuing to demand new medical certifications for each absence related to this condition, management acted"
            " contrary to the contractual agreement and imposed undue stress and administrative burden on the employee. \n\n This behavior constitutes a clear violation of the employee’s rights under the"
            " National Agreement and may also conflict with applicable federal laws and regulations that protect individuals managing chronic health conditions, including the Rehabilitation Act and FMLA"
            " provisions, depending on the specifics of the case. \n"
        },
        "The employer denied the use of annual leave in lieu of sick and no just cause was present to support the decision.": {
            "articles": ["Article 34 Section 5(A)"],
            "argument": "When the grievant requested to use annual leave in lieu of sick leave, management failed to comply with the National Agreement by neither approving the request nor providing a valid"
            " reason for the denial. The National Agreement allows employees to request annual leave instead of sick leave, and while management retains discretion to approve or deny such requests, that"
            " discretion is not unlimited or arbitrary. Any denial must be based on legitimate business reasons and should be communicated clearly to the employee upon request. \n\n In this case, the grievant"
            " made a reasonable and contractually permitted request to use their earned annual leave rather than sick leave. Management’s failure to honor this request—or to provide a valid justification for"
            " denying it—violates the principles of fairness and transparency outlined in the National Agreement. Moreover, this denial deprived the employee of the flexibility to manage their leave balances in"
            " a way that best suited their needs, without any documented operational necessity to support the denial. \n\n This constitutes a violation of the employee’s contractual rights, and management’s"
            " silence or refusal to explain the decision further underscores their failure to uphold the obligations set forth in the National Agreement. \n"
        },
        "Employee was on annual leave and became sick but was denied the ability to switch the annual leave to sick leave. Employee must have notified manager on the first day of illness.": {
            "articles": ["Article 34 Section 5(B)"],
            "argument": "Management violated the National Agreement by denying the grievant the opportunity to substitute sick leave for previously approved annual leave, despite the employee meeting all the"
            " outlined requirements in the National Agreement for making such a request. The National Agreement expressly provides employees the right to request a substitution of sick leave for annual leave"
            " if they become ill during scheduled annual leave, provided they follow the appropriate procedures and submit any required documentation. \n\n In this case, the grievant became ill during their"
            " period of approved annual leave and promptly complied with all procedural requirements necessary to convert the leave type—including timely notification and, if applicable, medical documentation."
            " By refusing to honor the request, management not only disregarded the employee’s rights under the National Agreement but also penalized the employee for an unforeseen medical issue during their"
            " earned time off. \n\n This denial resulted in an unjust forfeiture of sick leave that the employee was entitled to use, and it contradicts the intent and protections negotiated into the"
            " National Agreement. Management’s failure to approve the conversion of leave—despite the employee’s compliance—represents a clear contractual violation and an unreasonable exercise of discretion. \n"
        },
        "Denied advanced sick leave. Employee met the following conditions: \n"
        "  • Employee is eligible to earn sick leave. \n"
        "  • Employee's request does not exceed 30 workdays; or whatever lesser amount complies with applicable regulations (104 hrs bereavement). \n"
        "  • No reason to suggest the employee would not return to work. \n"
        "  • Employee has provided acceptable medical documentation. \n"
        "  • Employee is: \n"
        "       • Adopting a child. \n"
        "       • Employee or family member has a serious health condition. \n"
        "       • Planning arrangements necessitated by the death of a family member. \n"
        "       • To attend a funeral of a family member. \n"
        "  • Employee is not on a sick leave restriction. \n": {
            "articles": ["Article 34 Section 6(A)"],
            "argument": "Management violated the National Agreement by denying the grievant’s request for advanced sick leave, even though the employee met all the outlined conditions required for approval"
            " under the National Agreement. The Agreement clearly specifies the circumstances in which advanced sick leave shall be granted, provided the following conditions are satisfied: \n\n - The employee"
            " is eligible to earn sick leave; \n - The request does not exceed 30 workdays; \n - There is no indication the employee will not return to duty; \n - The employee has provided acceptable medical"
            " documentation supporting the need for the leave; \n - The employee is facing a qualifying event, such as the employee or a family member having a serious health condition, adopting a child,"
            " or making arrangements for or attending the funeral of a family member; and \n - The employee is not under a sick leave restriction. \n\n In the grievant’s case, all of these criteria were fully"
            " met. The medical documentation submitted was acceptable, the qualifying condition was clearly established, and no indication was given that the employee would not return to duty. Furthermore,"
            " the employee was not under any restrictions that would preclude consideration for advanced sick leave. \n\n By failing to approve the request under these conditions, management not only violated"
            " the explicit terms of the National Agreement but also deprived the employee of a contractually guaranteed benefit during a time of critical need. This denial was not only unjustified but also"
            " contrary to the principles of fairness and due process that the Agreement is designed to uphold. \n"
        },
        "Denied an employee advanced sick leave because they are probationary.": {
            "articles": ["Article 34 Section 6(B)"],
            "argument": "Management violated the National Agreement by denying the grievant’s request for advanced sick leave solely on the basis of their probationary status. While the National Agreement does"
            ' state that management may deny advanced sick leave to a probationary employee, this language does not grant automatic or unconditional authority to do so. The use of the term “may” indicates that'
            " each request must be evaluated on its individual merits, and any denial must be justified by legitimate and documented concerns beyond probationary status alone. \n\n In this case, the grievant"
            " satisfied all other criteria for approval of advanced sick leave under the National Agreement, including providing acceptable medical documentation and facing a qualifying event. By denying the"
            " request solely because the employee was probationary, and without demonstrating any additional justification—such as poor performance, attendance concerns, or uncertainty regarding return to"
            " duty—management failed to exercise proper discretion and instead relied on an overly broad and unsupported application of policy. \n\n This blanket denial approach contradicts the intent and"
            " protections outlined in the National Agreement and constitutes a violation of the employee’s contractual rights. Denials must be based on specific facts and not arbitrary categories such as"
            " employment status alone. \n"
        },
        "Denied advanced sick leave because of intended purposes. \n"
        "  • Advanced sick leave is not usable for only routine medical visits or minor illness": {
            "articles": ["Article 34 Section 6(C)"],
            "argument": "Management violated the National Agreement by denying the grievant’s request for advanced sick leave despite the request being made for a qualifying reason, not for a routine medical"
            " visit or minor illness. The National Agreement clearly states that advanced sick leave may be denied for non-serious conditions such as minor illnesses or routine check-ups. However, when an"
            " employee submits a request supported by acceptable medical documentation for a serious health condition—either for themselves or a qualifying family member—the request must be fairly evaluated in"
            " accordance with the criteria outlined in the National Agreement. \n\n In this case, the grievant submitted a request for advanced sick leave related to a legitimate, non-routine medical situation."
            " The nature of the request met the National Agreement’s qualifying conditions, and the employee was not under any sick leave restriction nor were there concerns regarding their return to duty."
            " By denying the request without justification and despite the fact that it did not fall under the limited exceptions (i.e., routine visits or minor ailments), management acted in direct"
            " contradiction to the intent of the National Agreement. \n\n Such a denial represents a clear violation of the employee’s rights, as it disregards both the contractual language and the purpose of"
            " the advanced sick leave provision—to ensure employees have access to paid leave in times of serious need. \n"
        },
        "The Agency failed to allow the employee to pay back the advanced sick leave balance due via earned sick leave or through a cash payment.": {
            "articles": ["Article 34 Section 6(D)"],
            "argument": "Management violated the National Agreement by failing to follow the required procedures for the repayment of advanced sick leave. The National Agreement clearly outlines that when an"
            " employee has been granted advanced sick leave, any repayment must occur through one of the two authorized methods: \n\n - Through the accrual of future earned sick leave until the full balance"
            " is restored; or \n - Through a cash payment to repay the amount owed. \n\n In this case, the grievant was prepared and willing to repay the advanced sick leave in accordance with one of the"
            " methods authorized by the National Agreement. However, management either denied the employee that opportunity or imposed alternate repayment terms not supported by the Agreement. This action"
            " constitutes a direct violation of the employee’s rights and a failure to uphold contractual obligations. \n\n By disregarding the specific repayment provisions outlined in the National Agreement,"
            " management created unnecessary confusion and potential financial harm for the employee, and failed to exercise good faith in administering leave policies.  \n"
        },
        "Management required medical information details about the nature of the individuals underlying medical condition to the employer.": {
            "articles": ["Article 34 Section 7(A)"],
            "argument": "Management violated the National Agreement by inappropriately requesting additional details regarding the grievant’s medical condition, despite the employee already providing the"
            " necessary documentation required under the National Agreement. The National Agreement clearly outlines a specific process that must be followed when management believes additional medical"
            " information is needed to support a sick leave request. \n\n This process includes a formal determination of insufficiency, followed by a written explanation of what additional information is"
            " required and why. It also includes protections to ensure that employee privacy and dignity are respected, and that only medically necessary information is requested. These safeguards are in place"
            " to prevent overreach and to ensure consistent, fair treatment across all employees. \n\n In this case, management bypassed or failed to adhere to that process and instead made an inappropriate"
            " request for more detailed personal medical information—a clear violation of both the spirit and the letter of the National Agreement. This intrusion into the employee’s private medical matters"
            " without procedural justification erodes trust, violates contractual protections, and undermines the employee’s rights under the Agreement. \n"
        },
        "Employer refused to provide a medical professional for the employee to turn required medical information over to after the employee requested. When specific medical information is required"
        ", including the diagnosis or prognosis of a medical condition, as part of an employee's request for sick leave, the employee may choose to provide that information only to a medical"
        " professional designated by the employer.": {
            "articles": ["Article 34 Section 7(A)"],
            "argument": "Management violated the National Agreement by refusing to comply with the employee’s right to submit sensitive medical information—such as a diagnosis or prognosis—directly to a"
            " medical professional designated by the employer, rather than to management personnel. The National Agreement explicitly allows employees to protect the confidentiality of their medical condition"
            " by choosing to submit such information only to a designated medical authority when more detailed documentation is requested. \n\n In this case, the grievant was willing to comply with the request"
            " for additional medical documentation but exercised their contractual right to do so through the appropriate channel—by asking that a medical professional be designated to receive the"
            " documentation. Management's failure or refusal to provide such a designee forced the employee into an unfair position: either share private medical details with non-medical personnel in violation"
            """ of their privacy rights, or risk denial of leave due to “non-compliance.” \n\n This refusal represents a clear violation of the employee's rights under the National Agreement, and undermines"""
            " important protections designed to balance the agency's need for information with the employee's right to confidentiality and dignity. \n"
        },
        "Management failed to treat the employee's medical information as confidential and released information to parties that did not need to know this information.": {
            "articles": ["Article 34 Section 7(B)"],
            "argument": "Management violated the National Agreement, as well as federal laws and regulations, by disclosing the grievant’s medical information to individuals who had no legitimate need to know."
            " The National Agreement clearly outlines that employee medical information is to be treated as strictly confidential and must only be shared with authorized personnel who require the information for"
            " legitimate administrative purposes. This standard aligns with broader legal requirements under the Privacy Act of 1974 and Office of Personnel Management (OPM) guidance concerning federal employee"
            " medical privacy. \n\n In this case, the grievant’s sensitive medical information was improperly shared with parties who were not involved in the leave approval process or otherwise had no"
            " business or legal need to access such information. This reckless handling of confidential medical details constitutes a serious breach of the employee’s right to privacy, and directly violates not"
            " only the National Agreement but also well-established federal privacy protections. \n\n Such a disclosure can cause irreparable harm, embarrassment, and mistrust within the workplace. Management"
            " must take immediate corrective action to prevent further harm to the employee and ensure all medical information is handled in strict compliance with the National Agreement and applicable federal"
            " privacy standards going forward. \n"
        },
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
        st.session_state.final_packet_buffer = None
        st.session_state.final_packet_name = None
        if not steward or not grievant:
            st.warning("Please fill out all required fields.")
        else:
            # Collect all arguments and articles
            full_argument = "\n\n".join(str(arg) for arg in selected_arguments)
            article_list = ", ".join(sorted(set(selected_articles)))
            filing_step = "Step Two - Streamlined Grievance"

            # All fields for the cover sheet
            form_data = {
                "Step": filing_step,
                "Steward": steward,
                "Grievant": grievant,
                "Issue Description": issue_description,
                "Desired Outcome": desired_outcome,
                "Articles of Violation": article_list,
                "Case ID": case_id,
                "Department Manager": dept_man,
                "Frontline Manager": flmanager,
                "Position": position,
                "Operation": workarea,
            }

            # Only the fields you want in the main PDF
            pdf_fields = [
                "Steward",
                "Grievant",
                "Issue Description",
                "Desired Outcome",
                "Articles of Violation"
            ]
            pdf_data = {k: form_data[k] for k in pdf_fields if k in form_data}

            grievance_type = st.session_state.get("grievance_type", "AWOL Grievance")
            cover_sheet_buffer = create_cover_sheet(form_data, grievance_type)  # Returns BytesIO
            base_pdf_buffer = generate_pdf(pdf_data, full_argument)            # Returns BytesIO

            # --- Merge PDFs: cover sheet first ---
            merger = PdfMerger()
            merger.append(cover_sheet_buffer)
            merger.append(base_pdf_buffer)

            # Merge all uploaded files
            if uploaded_files:
                for file in uploaded_files:
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

            # Write merged PDF to a BytesIO buffer for download
            merged_buffer = BytesIO()
            merger.write(merged_buffer)
            merger.close()
            merged_buffer.seek(0)

            st.session_state.final_packet_buffer = merged_buffer
            st.session_state.final_packet_name = f"{grievant.replace(' ', '_')}_AWOL_Grievance.pdf"

    # --- Download button ---
    if (
        "final_packet_buffer" in st.session_state
        and st.session_state.final_packet_buffer is not None
        and st.session_state.final_packet_name
    ):
        st.download_button(
            "📄 Download AWOL Grievance PDF",
            st.session_state.final_packet_buffer.getvalue(),
            file_name=st.session_state.final_packet_name
        )
