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
    /* Fix for button text visibility */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
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
    st.sidebar.title("🏢 Mainland Group")
    # New Role Selector
    role_choice = st.sidebar.radio("Select Login Role:", ["User", "Admin"])
    user_input = st.sidebar.text_input("Enter First Name or Admin Password", type="password")

    if st.sidebar.button("ENTER"): # Added label to button
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
    # 5. USER INTERFACE
    if st.session_state.role == "User":
        st.sidebar.info(f"Welcome, {st.session_state.user_name}")
        choice = st.sidebar.radio("Go To:", ["Submit Work Plan", "My History"])

        if choice == "Submit Work Plan":
            st.title("📝 New Work Plan Submission")
            with st.form("user_form"):
                # Locked the name selection so it cannot be changed
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
                            "Staff Name": st.session_state.user_name, # Forced from session
                            "Date": str(s_date), "Work Plan": s_plan,
                            "Hours left to completion": s_left, "Hours planned for this week": s_planned,
                            "Comment": s_comm, "Status": "Pending"
                        }])
                        current_df = conn.read(worksheet="Tracker")
                        updated_df = pd.concat([current_df, new_entry], ignore_index=True)
                        conn.update(worksheet="Tracker", data=updated_df)
                        st.success("Submitted! Status: 🟡 Pending")
                    else:
                        st.warning("Please check the confirmation box first.")

        elif choice == "My History":
            st.title("🕒 Submission History")
            all_data = conn.read(worksheet="Tracker")
            my_data = all_data[all_data['Staff Name'] == st.session_state.user_name]
            for i, row in my_data.iterrows():
                stat = row['Status']
                color = "🟡" if stat == "Pending" else "🟢" if stat == "Approved" else "🔴"
                with st.expander(f"{color} Plan for {row['Date']} - {stat}"):
                    st.write(f"**Plan:** {row['Work Plan']}")
                    st.write(f"**Hours Left:** {row['Hours left to completion']}")
                    st.write(f"**Comment:** {row['Comment']}")

    # 6. ADMIN INTERFACE
    elif st.session_state.role == "Admin":
        st.title("👨‍💼 Admin Dashboard")
        df = conn.read(worksheet="Tracker")
        pending = df[df['Status'] == "Pending"]

        if pending.empty:
            st.info("No pending submissions to review.")
        else:
            for idx, row in pending.iterrows():
                st.subheader(f"Request from: {row['Staff Name']}")
                st.write(f"**Date:** {row['Date']} | **Hours:** {row['Hours planned for this week']}")
                st.write(f"**Plan:** {row['Work Plan']}")
                
                # Fixed column error: st.columns(2) instead of 5
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve", key=f"a{idx}"):
                    df.at[idx, 'Status'] = "Approved"
                    conn.update(worksheet="Tracker", data=df)
                    st.rerun()
                if c2.button("❌ Decline", key=f"d{idx}"):
                    df.at[idx, 'Status'] = "Declined"
                    conn.update(worksheet="Tracker", data=df)
                    st.rerun()
                st.write("---")

    # 7. LOGOUT
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.rerun()
