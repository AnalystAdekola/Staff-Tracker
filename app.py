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
    
    /* FIX FOR BUTTON LABEL VISIBILITY */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px;
        border: 2px solid #2E7D32;
        padding: 0.6rem 2rem;
        font-weight: bold !important;
        font-size: 16px !important;
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
    "Aminat Aliu", "Alli Ibrahim", "Aworinde Opeyemi"
]

# 3. INITIALIZE CONNECTION & SESSION
conn = st.connection("gsheets", type=GSheetsConnection)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = None

# 4. LOGIN INTERFACE
if not st.session_state.logged_in:
    st.title("🤝 WELCOME TO MAINLAND")
    st.sidebar.title("🏢 Portal Login")
    role_choice = st.sidebar.radio("Login as:", ["User", "Admin"])
    user_input = st.sidebar.text_input("Enter Credentials", type="password")

    # FIXED BUTTON LABEL
    if st.sidebar.button("ENTER"): 
        if role_choice == "Admin" and user_input == "MainlandTep":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.rerun()
        elif role_choice == "User" and any(user_input.lower() in name.lower() for name in staff_list):
            full_name = next(name for name in staff_list if user_input.lower() in name.lower())
            st.session_state.logged_in = True
            st.session_state.role = "User"
            st.session_state.user_name = full_name
            st.rerun()
        else:
            st.sidebar.error("Invalid details.")
else:
    # GLOBAL SIDEBAR OPTIONS
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    # 3. TOGGLE OPTION FOR ADMIN
    if st.session_state.role == "Admin":
        admin_mode = st.sidebar.toggle("Switch to User View", value=False)
        current_view = "User" if admin_mode else "Admin"
    else:
        current_view = "User"

    # 5. USER INTERFACE (Submission & History)
    if current_view == "User":
        # Handle Admin acting as User
        display_name = st.session_state.user_name if st.session_state.user_name else "Admin (Testing)"
        st.sidebar.info(f"Viewing as: {display_name}")
        
        choice = st.sidebar.radio("Menu", ["Submit Work Plan", "My History"])

        if choice == "Submit Work Plan":
            st.title("📝 New Work Plan")
            with st.form("user_form"):
                st.write(f"Staff: **{display_name}**")
                s_date = st.date_input("Date", date.today())
                s_plan = st.text_area("Work Plan Details")
                c1, c2 = st.columns(2)
                s_left = c1.number_input("Hours left to completion", min_value=0)
                s_planned = c2.number_input("Hours planned for this week", min_value=0)
                s_comm = st.text_input("Comment")
                
                confirm = st.checkbox("Confirm details")
                submit_btn = st.form_submit_button("Submit Plan")

                if submit_btn and confirm:
                    new_entry = pd.DataFrame([{
                        "Staff Name": display_name,
                        "Date": str(s_date), 
                        "Work Plan": s_plan,
                        "Hours left to completion": s_left, 
                        "Hours planned for this week": s_planned,
                        "Comment": s_comm
                    }])
                    # 4. IMMEDIATE REFLECTION
                    current_df = conn.read(worksheet="Tracker", ttl=0) # ttl=0 forces fresh data
                    updated_df = pd.concat([current_df, new_entry], ignore_index=True)
                    conn.update(worksheet="Tracker", data=updated_df)
                    st.success("Submitted! Check history or dashboard.")
                    st.balloons()

        elif choice == "My History":
            st.title("🕒 Your History")
            # Force refresh from Google Sheets
            my_history = conn.read(worksheet="Tracker", ttl=0)
            my_history = my_history[my_history['Staff Name'] == display_name]
            st.table(my_history[::-1]) # Show newest first

    # 6. ADMIN INTERFACE (No Status Column)
    elif current_view == "Admin":
        st.title("👨‍💼 Admin Master Dashboard")
        # 2. READ DATA WITHOUT STATUS
        df = conn.read(worksheet="Tracker", ttl=0)
        
        if not df.empty:
            # Explicitly remove 'Status' column if it exists in the sheet
            if 'Status' in df.columns:
                df = df.drop(columns=['Status'])
            
            search = st.text_input("Search Staff Name")
            if search:
                df = df[df['Staff Name'].str.contains(search, case=False)]
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found in the Tracker.")
