import streamlit as st
import datetime
import holidays
import tempfile
import os
from util import draw_wrapped_section, generate_pdf, convert_to_pdf, calculate_fbd

def render_annual():
  
