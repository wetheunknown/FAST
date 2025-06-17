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
from render_awol_issue import render_awol
from render_annual_issue import render_annual
from util import wrap_text_to_width,draw_wrapped_section, generate_pdf, convert_to_pdf, calculate_fbd

MAX_UPLOADS = 10

st.title("Federal Advocacy Support Toolkit \n FAST - Provided by NTEU CH. 66")

st.subheader("📌 Select Grievance Type")

grievance_type = st.radio(
    "Choose the type of grievance you'd like to file:",
    ["Annual Appraisal", "AWOL - Annual/Sick Leave", "Telework (Coming Soon)", "AWS (Coming Soon)", "Work Schedule/ Hours of Work (Coming Soon)"],
    index=0
)

if grievance_type == "Annual Appraisal":
    render_annual()

if grievance_type == "AWOL - Annual/Sick Leave":
    render_awol()
