import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta

# 1. PAGE SETUP & THEME
st.set_page_config(page_title="Mainland Group Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFDD0; }
    h1, h2, h3, p, span, label { color: #2E7D32 !important; }
    
    .stButton>button, .stFormSubmitButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        border: 3px solid #2E7D32;
        padding: 0.6rem 2rem;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        background-color: #F0F0F0 !important;
        border-color: #1B5E20;
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
if 'tasks_to_submit' not in st.session_state:
    st.session_state.tasks_to_submit = []

# 4. LOGIN INTERFACE
if not st.session_state.logged_in:
    st.title("🤝 WELCOME TO MAINLAND")
    st.sidebar.title("🏢 Portal Login")
    role_choice = st.sidebar.radio("Login as:", ["User", "Admin"])
    user_input = st.sidebar.text_input("Enter Credentials", type="password")

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
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    
    if st.session_state.role == "Admin":
        admin_mode = st.sidebar.toggle("Switch to User View", value=False)
        current_view = "User" if admin_mode else "Admin"
    else:
        current_view = "User"

    # 5. USER INTERFACE (Multi-Task Board)
    if current_view == "User":
        display_name = st.session_state.user_name if st.session_state.user_name else "Admin (Testing)"
        st.sidebar.info(f"User: {display_name}")
        choice = st.sidebar.radio("Menu", ["Submit Work Plan", "My History"])

        if choice == "Submit Work Plan":
            st.title("📝 Multi-Task Work Plan")
            
            with st.expander("➕ Add a Task to your List", expanded=True):
                with st.form("task_creator", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    # Monday & Saturday Logic
                    s_date = col_a.date_input("Start Date (Must be Monday)")
                    e_date = col_b.date_input("End Date (Must be Saturday)")
                    
                    s_plan = st.text_area("Task Description")
                    c1, c2 = st.columns(2)
                    s_left = c1.number_input("Hours left to completion", min_value=0)
                    s_planned = c2.number_input("Hours planned for this week", min_value=0)
                    s_comm = st.text_input("Comment")
                    
                    add_task = st.form_submit_button("ADD TO LIST")
                    
                    if add_task:
                        if s_date.weekday() != 0: # 0 is Monday
                            st.error("Error: Start Date must be a Monday.")
                        elif e_date.weekday() != 5: # 5 is Saturday
                            st.error("Error: End Date must be a Saturday.")
                        elif not s_plan:
                            st.error("Please enter a description.")
                        else:
                            st.session_state.tasks_to_submit.append({
                                "Staff Name": display_name,
                                "Start Date": str(s_date),
                                "End Date": str(e_date),
                                "Work Plan": s_plan,
                                "Hours Left": s_left,
                                "Hours Planned": s_planned,
                                "Comment": s_comm,
                                "Submission Date": str(date.today())
                            })
                            st.success("Task added to pending list below!")

            if st.session_state.tasks_to_submit:
                st.write("### 📋 Your Pending Tasks")
                pending_df = pd.DataFrame(st.session_state.tasks_to_submit)
                st.dataframe(pending_df)
                
                col_btn1, col_btn2 = st.columns([1, 5])
                if col_btn1.button("🗑️ CLEAR LIST"):
                    st.session_state.tasks_to_submit = []
                    st.rerun()
                
                if col_btn2.button("🚀 SUBMIT ALL TASKS TO PORTAL"):
                    current_df = conn.read(worksheet="Tracker", ttl=0)
                    updated_df = pd.concat([current_df, pending_df], ignore_index=True)
                    conn.update(worksheet="Tracker", data=updated_df)
                    st.session_state.tasks_to_submit = []
                    st.success("All tasks submitted successfully!")
                    st.balloons()

        elif choice == "My History":
            st.title("🕒 Your History")
            my_history = conn.read(worksheet="Tracker", ttl=0)
            my_history = my_history[my_history['Staff Name'] == display_name]
            st.dataframe(my_history[::-1], use_container_width=True)

    # 6. ADMIN INTERFACE (Date Range Filter)
    elif current_view == "Admin":
        st.title("👨‍💼 Admin Master Dashboard")
        df = conn.read(worksheet="Tracker", ttl=0)
        
        if not df.empty:
            st.subheader("Filters")
            col_f1, col_f2 = st.columns(2)
            
            unique_names = ["All"] + sorted(df["Staff Name"].unique().tolist())
            name_filter = col_f1.selectbox("Filter by Name", unique_names)
            
            # Date Range Filter
            date_range = col_f2.date_input("Filter by Period (Start - End)", value=[])

            filtered_df = df.copy()
            if name_filter != "All":
                filtered_df = filtered_df[filtered_df["Staff Name"] == name_filter]
            
            if len(date_range) == 2:
                start_f, end_f = date_range
                # Ensure Start Date column is converted to datetime for comparison
                filtered_df['Start Date Temp'] = pd.to_datetime(filtered_df['Start Date'])
                filtered_df = filtered_df[
                    (filtered_df['Start Date Temp'].dt.date >= start_f) & 
                    (filtered_df['Start Date Temp'].dt.date <= end_f)
                ]
                filtered_df = filtered_df.drop(columns=['Start Date Temp'])
            
            st.write("---")
            st.write(f"Showing **{len(filtered_df)}** records")
            st.dataframe(filtered_df, use_container_width=True)
