import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. PAGE SETUP & THEME
st.set_page_config(page_title="Mainland Group Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFDD0; }
    h1, h2, h3, p, span, label { color: #2E7D32 !important; }
    
    /* BUTTON STYLING: RED FILL WITH BLACK TEXT */
    .stButton>button, .stFormSubmitButton>button {
        background-color: #FF0000 !important; /* Pure Red */
        color: #000000 !important;             /* Pure Black */
        border-radius: 10px;
        border: 2px solid #000000;
        padding: 0.6rem 2rem;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-transform: uppercase;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Ensure hover effect doesn't wash out the black text */
    .stButton>button:hover {
        color: #000000 !important;
        border: 2px solid #2E7D32;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>textarea {
        background-color: white !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. STAFF DATA
staff_list = [
    "Ann Obieje", "Olaniran Paul", "Seun Olowolafe", "Grace Ogundaini", 
    "Ayokunle Omotayo", "Joy Ifeanyi", "Dayo Gregory", "Daniel Ayala", 
    "Adekola Adeleke", "Yusuf Oluwaseun", "Stephen Olabinjo", "Chinenye Agwuncha", 
    "Esumo Esumo", "Ejiro Ujara", "Sekinat Ojeniyi", "CHIAMAKA EZEAGU", 
    "Aminat Aliu", "Alli Ibrahim", "Aworinde Opeyemi
