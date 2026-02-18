import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. PAGE SETUP & THEME
st.set_page_config(page_title="Mainland Group Portal", layout="wide")

# Custom CSS for colors and button text visibility
st.markdown("""
    <style>
    .stApp { background-color: #FFFDD0; }
    h1, h2, h3, p, span, label { color: #2E7D32 !important; }
    
    /* Fix for button text - forced white and visible */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
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
    # 6. WELCOME SPLASH PAGE
    st.title("🤝 WELCOME TO MAINLAND")
    st.subheader("Mainland Group Staff Management Portal")
    st.write("Please use the sidebar to log in.")
    
    st.sidebar.title("🏢 Login Portal")
    role_choice = st.sidebar.radio("Select Login Role:", ["User", "Admin"])
    user_input = st.sidebar.text_input("Enter First Name or Admin Password", type="password")

    # 2. FIXED BUTTON LABEL
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
            st.sidebar.error("Access Denied. Please check your credentials.")
else:
    # Sidebar Logout Button (Always available when logged in)
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.rerun()

    # 5. USER INTERFACE
    if st.session_state.role == "User":
        st.sidebar.info(f"Welcome, {st.session_state.user_name}")
        choice = st.sidebar.radio("Go To:", ["Submit Work Plan", "My History"])

        if choice == "Submit Work Plan":
            st.title("📝 New Work Plan Submission")
            with st.form("user_form"):
                st.info(f"Logged in as: {st.session_state.user_name}")
                s_date = st.date_input("Select Date", date.today())
                s_plan = st.text_area("What is your work plan?")
                col1, col2 = st.columns(2)
                s_left = col1.number_input("Hours left to completion", min_value=0)
                s_planned = col2.number_input("Hours planned for this week", min_value=0)
                s_comm = st.text_input("Comment")
                
                st.write("---")
                confirm = st.checkbox("I am sure I want to submit this plan.")
                submit_btn = st.form_submit_button("Submit Plan")

                if submit_btn:
                    if confirm:
                        new_entry = pd.DataFrame([{
                            "Staff Name": st.session_state.user_name,
                            "Date": str(s_date), 
                            "Work Plan": s_plan,
                            "Hours left to completion": s_left, 
                            "Hours planned for this week": s_planned,
                            "Comment": s_comm
                        }])
                        current_df = conn.read(worksheet="Tracker")
                        # Combine and update
                        updated_df = pd.concat([current_df, new_entry], ignore_index=True)
                        conn.update(worksheet="Tracker", data=updated_df)
                        st.success("Submitted successfully!")
                        # 3. FORCE REFRESH SO IT REFLECTS IN HISTORY IMMEDIATELY
                        st.balloons()
                    else:
                        st.warning("Please check the confirmation box first.")

        elif choice == "My History":
            st.title("🕒 Your Submission History")
            all_data = conn.read(worksheet="Tracker")
            # Filter just for this staff member
            my_data = all_data[all_data['Staff Name'] == st.session_state.user_name]
            
            if my_data.empty:
                st.write("No history found.")
            else:
                for i, row in my_data[::-1].iterrows(): # Shows newest first
                    with st.expander(f"Plan for {row['Date']}"):
                        st.write(f"**Plan:** {row['Work Plan']}")
                        st.write(f"**Hours Left:** {row['Hours left to completion']}")
                        st.write(f"**Comment:** {row['Comment']}")

    # 4. ADMIN INTERFACE
    elif st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Master Dashboard")
        st.write("Viewing all staff submissions (Approval system removed).")
        
        df = conn.read(worksheet="Tracker")
        
        if df.empty:
            st.info("The spreadsheet is currently empty.")
        else:
            # Add a search/filter to Admin view
            search_query = st.text_input("Search by Staff Name")
            if search_query:
                df = df[df['Staff Name'].str.contains(search_query, case=False)]
            
            st.dataframe(df, use_container_width=True)
