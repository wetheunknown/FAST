import streamlit as st
import datetime
import holidays
import tempfile
import os
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
            " Therefore, management’s insistence on the literal inclusion of the word “incapacitated” or any other language not explicitly required by the National Agreement constitutes an unauthorized"
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
            "argument": "     According to the NA, an employee is supposed to be allowed up to 30-days after the date of request made by the employer for medical certification if it is not practicable"
            " to get it sooner. Management should not be requiring this paperwork prior to this deadline and by doing so have violated the empolyee's rights. \n"
        },
        "Employer required an employee to provide medical documentation because of:\n"
        "  • A specific work day or work time. \n"
        "  • High volume day \n"
        "  • Black out day \n"
        "  • Critical day": {
            "articles": ["Article 34 Section 3(E)"],
            "argument": "     The NA clearly specifies that management will not require medical documenation based on a specific workday or specific work time. Examples of this would be high volume"
            " days, blackout days, or critical days. Management should not have requested medical documentation for the absence and the employee should not have been denied for not providing the medical"
            " certificate.\n"
        },
        "The employer placed the employee on a sick leave restriction but failed to provide oral counsel to the employer prior to implementation to allow the employee an opportunity to not"
        " be placed on one.": {
            "articles": ["Article 34 Section 4(A)(1)"],
            "argument": "     The NA lays out the procedures for management on issuing a sick leave restriction to an employee. It is a violation of the employee's rights to not have been given an"
            " oral counseling prior to the issuance of a sick leave restriction. Management should allow for this oral counsel prior to the issuance of a sick leave restriction to allow the employee"
            " an opportunity to correct the behavior. \n"
        },
        "Employee has been placed on a sick leave restriction that has exceeded the maximum limitation of allowed time for a sick leave restriction.": {
            "articles": ["Article 34 Section 4(A)(3)"],
            "argument": "     The maximum amount of time that an employee can be placed under a sick leave restriction at a time is clearly defined in the NA. The maximum amount of time is 6-months."
            " Going beyond the allowed 6-months time on a sick leave restriction is a violation of the employee's rights as laid out by the NA.\n"
        },
        "The employee was placed on a sick leave restriction that utilized the employee's usage of approved annual leave and/or leave under FMLA as reasoning rather than absences due to illnesses.": {
            "articles": ["Article 34 Section 4(A)(4)"],
            "argument": "     A sick leave restriction is supposed to only take into account for the absences that an employee has had for illnesses. Utilizing annual leave or FMLA leave in the sick"
            " leave restriction is a violation of the employee's rights as laid out by the NA. \n"
        },
        "Employee was denied the usage of annual leave or sick leave based on a sick leave restriction.": {
            "articles": ["Article 34 Section 4(A)(4)"],
            "argument": "     A sick leave restriction does not prevent the usage of annual leave or FMLA leave per the NA. Denying the use of any leave other than sick leave based on the sick"
            " leave restriction is a violation of the employee's rights as laid out in the NA. \n"
        },
        "Employee was forced to provide medical documentation for being released from duty due to illness and did not have a sick leave restriction in place.": {
            "articles": ["Article 34 Section 4(B)"],
            "argument": "     It is inappropriate for management to to request additional documentation from an employee who left early from their scheduled TOD and was not on a sick leave"
            " restriction. The self-certification from the employee for this partial day should have been substatiating evidence for the approval of sick leave and would not have warranted management"
            " the rights to ask for additional documentation. By doing so, management has failed to comply with the NA and have violated the rights of the employee.\n"
        },
        "Employee has provided to the Agency proof of a chronic condition, is not on a sick leave restriction, and is still being required to furnish medical documentation for the time off for"
        " the chronic condition. \n"
        "  • A chronic condition does not necessarily mean that it requires medical treatment.": {
            "articles": ["Article 34 Section 4(C)"],
            "argument": "     The NA clearly states that when an employee has a chronic condition that requires continuing absences to occur and is not on a sick leave restriction that management will"
            f" not continually require medical documentation to be furnished. By making {grievant} continually furnish medical certifications for these absences, it is a violation of their rights as"
            " laid out by the NA, applicable laws, and regulations. \n"
        },
        "The employer denied the use of annual leave in lieu of sick and no just cause was present to support the decision.": {
            "articles": ["Article 34 Section 5(A)"],
            "argument": f"     When {grievant} requested the use of annual leave in lieu of utilizing sick leave, management should have granted them this or provided them with the reasoning"
            " to justify the denial. By failing to do this, management has violated the NA and this employee's rights. \n"
        },
        "Employee was on annual leave and became sick but was denied the ability to switch the annual leave to sick leave. Employee must have notified manager on the first day of illness.": {
            "articles": ["Article 34 Section 5(B)"],
            "argument": "     Denying an employee the opportunity to switch their annual leave to sick leave after the employee complied with the outlined requirements to do so in the NA is a violation"
            " of the employee's rights. Management should allow an individual who requested annual leave and got sick during that time to switch their time from annual leave to sick leave.\n"
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
            "argument": "     The NA is very clear on when advanced sick leave will be given to an employee. The requirements to be given advanced sick leave is that the employee is eligible to earn"
            " sick leave, requested time does not exceed 30 workdays, no reason to believe the employee would not return to work, the employee has provided acceptable medical documentation for the need"
            " of advanced sick leave, employee is facing a qualifying event, and the employee is not under a sick leave restriction. A qualifying event is listed as adopting a chile, the employee"
            " or family member has a serious health condition, make arangements necessitated by a death of a family member or to attend a funeral of a family member. Denying the request when all of these"
            " have been met is a violation of the employee's rights.\n"
        },
        "Denied an employee advanced sick leave because they are probationary.": {
            "articles": ["Article 34 Section 6(B)"],
            "argument": "     The NA states that when an employee is on probation, that it may deny advanced sick leave. Denying a probationary employee the opportunity for advanced sick leave must be"
            " justifiable beyond just being probationary. By denying a probationary employee just based on the facts that they are probationary, is a violation of the NA and the employee's rights. \n"
        },
        "Denied advanced sick leave because of intended purposes. \n"
        "  • Advanced sick leave is not usable for only routine medical visits or minor illness": {
            "articles": ["Article 34 Section 6(C)"],
            "argument": "     A request for advanced sick leave should not be denied because of the intended purposes unless the request was made for routine medical visits or minor illness."
            " By management denying the request for advanced leave when the employee did not request the leave for a routine medical visit or a minor illness, management has violated the employee's"
            " right as given by the NA.\n"
        },
        "The Agency failed to allow the employee to pay back the advanced sick leave balance due via earned sick leave or through a cash payment.": {
            "articles": ["Article 34 Section 6(D)"],
            "argument": "     It is a violation of an employee's rights to not allow an employee to repay the advanced sick leave any other way than described in the NA. Management should"
            f" allow {grievant} to pay back the amount borrowed for the advanced sick leave either by utilization of earned sick leave hours or through a cash payment. \n"
        },
        "Management required medical information details about the nature of the individuals underlying medical condition to the employer.": {
            "articles": ["Article 34 Section 7(A)"],
            "argument": "     It is inappropriate and a violation of an employees' rights to have management request additional details about a medical condition that the employee has. The NA"
            " outlines the process needed to follow if additional medical information is required for the purposes of sick leave. This process should be followed by management to stay compliant with the NA.\n"
        },
        "Employer refused to provide a medical professional for the employee to turn required medical information over to after the employee requested. When specific medical information is required"
        ", including the diagnosis or prognosis of a medical condition, as part of an employee's request for sick leave, the employee may choose to provide that information only to a medical"
        " professional designated by the employer.": {
            "articles": ["Article 34 Section 7(A)"],
            "argument": "     When specific medical information is required, including the diagnosis or prognosis of a medical condition, as part of an employee's request for sick leave, the EE may"
            " choose to provide that information only to a medical professional designated by the employer. It is a violation of the employee's rights for management to refuse to comply by providing"
            " a medical professional for the employee to handover documentation about their medical information. \n"
        },
        "Management failed to treat the employee's medical information as confidential and released information to parties that did not need to know this information.": {
            "articles": ["Article 34 Section 7(B)"],
            "argument": "     Management failed to comply with the NA, laws, and regulations surrounding the protection of federal worker's and the privacy of medical information. By management"
            " sharing {grievant}'s medical information with parties that did not need this information, management violated the employee's right to privacy as well as the rights granted under the NA."
            " Management should not allow this violation to continue and should take all neccessary precautions to protect the employee from undue harm from this violation of the employee's privacy.\n"
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
        if not steward or not grievant:
            st.warning("Please fill out all required fields.")
        else:
            full_argument = "\n\n".join(str(arg) for arg in selected_arguments)
            article_list = ", ".join(sorted(set(selected_articles)))
            
            filing_step = str("Step Two - Streamlined Grievance")
            
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
                "Operation": workarea
            }
            
            pdf_data = {
                "Steward": steward,
                "Grievant": grievant,
                "Issue Description": issue_description,
                "Desired Outcome": desired_outcome,
                "Articles of Violation": article_list
            }
            
            grievance_type = st.session_state.get("grievance_type", "AWOL Grievance")
    
            cover_sheet = create_cover_sheet(form_data, grievance_type)
            awol_pdf = generate_pdf(pdf_data, full_argument)  # Should return a BytesIO!
            final_pdf_buffer = merge_pdfs(cover_sheet, awol_pdf)
    
            st.download_button(
                "📄 Download AWOL Grievance PDF",
                final_pdf_buffer.getvalue(),  # use getvalue() for bytes
                file_name=f"{grievant.replace(' ', '_')}_AWOL_Grievance.pdf"
            )
