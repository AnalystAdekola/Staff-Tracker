import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta

# 1. PAGE SETUP & THEME
st.set_page_config(page_title="Lagos Apps Group Portal", layout="wide")

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

# 2. STAFF DATA & REVIEWER MAPPINGS
staff_list = [
    "UDOOKON HELEN XAVIER", "EKENE KINGSLEY", "STEPHEN OLABINJO", "SAMUEL ONYEKACHI UMEZURIKE",
    "OGUNDAINI GRACE ODUNAYO", "ADEKOLA ADELEKE", "OMOTAYO GREGORY TEMIDAYO", "KABIR ODUNAYO ADELEKE",
    "EJIROGHENE OMOTEKORO UJARA", "OLANIRAN PAUL OLUWADAMILERE", "ESUMO OKON ESUMO", "AYOKUNLE OMOTAYO ABIODUN",
    "OLOWOLAFE OLUWASEUN JOSEPH", "ALLI IBRAHIM ABAYOMI", "DURAND YETUNDE", "OLAMIDE ABDULHAKEEM AKINOLA",
    "CONFIDENCE EDWIN OLEKAUWA", "FUNMILAYO NAOMI NEJO", "ANUOLUWAPO TIWALADE BOBADE", "JOSEPH SEUN EMMANUEL",
    "OPEYEMI ENOCH AWORINDE", "LAWAL ABEEB", "WISDOM CHINOMSO UMEZURIKE", "FRIDAY GABRIEL", "BELOVED",
    "SOLAR ENGINEERS & INSTALLERS", "OWOLABI PETER OLOTU", "WAHAB AZEEZ", "IBRAHIM KAZEEM YUSUF",
    "BIODUN RAHEEM BALOGUN", "NWABUDIKE ROBERT CHIBUZOR", "ACHOLONU MARTINS", "OLAKUNLE ABIODUN ONI",
    "YUSUF TAJUDEEN OLUWASEUN", "OBIEJE ANN CHIKA", "AYALA DANIEL OMOKAGBO", "CHINENYE BLESSING AGWUNCHA",
    "JOY AMARACHI IFEANYI", "OJENIYI SEKINAT MOTUNRAYO", "ALIU AMINAT", "OLUWATOMISIN SAMSON ADEBARA",
    "EZEAGU CHIAMAKA VANESSA", "ANICHEBE AUGUSTINA UCHE", "MARY AKUOMA IFOGAH", "ODUNG ELIZABETH JAMES",
    "AWONIYI SUNBO TOSIN", "AKPAN INIOBONG INYANG", "OKORO CHARITY CHINYERE", "BASSEY IKWO", "ONUOHA ANNAGRACE TOCHI"
]

reviewer_mapping = {
    "JIDE OLATEJU": ["JIDE OLATEJU", "UDOOKON HELEN XAVIER", "EKENE KINGSLEY", "STEPHEN OLABINJO", "SAMUEL ONYEKACHI UMEZURIKE", "OGUNDAINI GRACE ODUNAYO", "ADEKOLA ADELEKE", "OMOTAYO GREGORY TEMIDAYO", "KABIR ODUNAYO ADELEKE", "EJIROGHENE OMOTEKORO UJARA", "OLANIRAN PAUL OLUWADAMILERE", "ESUMO OKON ESUMO", "AYOKUNLE OMOTAYO ABIODUN", "OLOWOLAFE OLUWASEUN JOSEPH", "ALLI IBRAHIM ABAYOMI", "DURAND YETUNDE", "OLAMIDE ABDULHAKEEM AKINOLA"],
    "EJIROGHENE UJARA": ["EJIROGHENE UJARA", "ADEKOLA ADELEKE", "OLANIRAN PAUL OLUWADAMILERE", "DURAND YETUNDE", "CONFIDENCE EDWIN OLEKAUWA", "FUNMILAYO NAOMI NEJO", "ANUOLUWAPO TIWALADE BOBADE", "JOSEPH SEUN EMMANUEL", "WISDOM CHINOMSO UMEZURIKE", "OPEYEMI ENOCH AWORINDE", "LAWAL ABEEB", "FRIDAY GABRIEL", "BELOVED", "SOLAR ENGINEERS & INSTALLERS"],
    "BARR ESUMO ESUMO": ["BARR ESUMO ESUMO", "UDOOKON HELEN XAVIER", "OWOLABI PETER OLOTU", "SAMUEL ONYEKACHI UMEZURIKE", "WAHAB AZEEZ", "IBRAHIM KAZEEM YUSUF", "BIODUN RAHEEM BALOGUN", "NWABUDIKE ROBERT CHIBUZOR", "ACHOLONU MARTINS", "OLAKUNLE ABIODUN ONI", "OMOTAYO GREGORY TEMIDAYO", "KABIR ODUNAYO ADELEKE"],
    "STEPHEN OLABINJO": ["STEPHEN OLABINJO", "YUSUF TAJUDEEN OLUWASEUN", "OBIEJE ANN CHIKA", "AYALA DANIEL OMOKAGBO", "CHINENYE BLESSING AGWUNCHA", "JOY AMARACHI IFEANYI", "OJENIYI SEKINAT MOTUNRAYO", "ALIU AMINAT", "OLUWATOMISIN SAMSON ADEBARA", "EZEAGU CHIAMAKA VANESSA"],
    "GRACE OGUNDAINI": ["GRACE OGUNDAINI", "AYOKUNLE OMOTAYO ABIODUN", "OLOWOLAFE OLUWASEUN JOSEPH", "ALLI IBRAHIM ABAYOMI", "OLAMIDE ABDULHAKEEM AKINOLA", "CONFIDENCE EDWIN OLEKAUWA", "FRIDAY GABRIEL"],
    "ANALYST": ["ANALYST", "ANICHEBE AUGUSTINA UCHE", "MARY AKUOMA IFOGAH", "ODUNG ELIZABETH JAMES", "AWONIYI SUNBO TOSIN", "AKPAN INIOBONG INYANG", "OKORO CHARITY CHINYERE", "BASSEY IKWO", "ONUOHA ANNAGRACE TOCHI", "SOLAR ENGINEERS & INSTALLERS"]
}

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
    st.title("🤝 WELCOME TO LAGOS APPS")
    st.sidebar.title("🏢 Portal Login")
    role_choice = st.sidebar.radio("Login as:", ["User", "Reviewer", "Admin"])
    user_input = st.sidebar.text_input("Enter Credentials (Password/Name)", type="password")

    if st.sidebar.button("ENTER"): 
        if role_choice == "Admin" and user_input == "LagosTep":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.rerun()
        elif role_choice == "Reviewer":
            reviewer_found = next((name for name in reviewer_mapping.keys() if name.split()[0].upper() == user_input.upper() or (name=="ANALYST" and user_input.upper()=="ANALYST")), None)
            if reviewer_found:
                st.session_state.logged_in = True
                st.session_state.role = "Reviewer"
                st.session_state.user_name = reviewer_found
                st.rerun()
            else:
                st.sidebar.error("Invalid Reviewer Credentials.")
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
        st.session_state.tasks_to_submit = []
        st.rerun()
    
    current_view = st.session_state.role

    # 5. USER INTERFACE
    if current_view == "User":
        st.sidebar.info(f"User: {st.session_state.user_name}")
        choice = st.sidebar.radio("Menu", ["Submit Work Plan", "My History"])

        if choice == "Submit Work Plan":
            st.title("📝 Multi-Task Work Plan")
            with st.expander("➕ Add a Task to your List", expanded=True):
                with st.form("task_creator", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    s_date = col_a.date_input("Start Date (Must be Sunday)")
                    e_date = col_b.date_input("End Date (Must be Saturday)")
                    s_plan = st.text_area("Task Description")
                    c1, c2 = st.columns(2)
                    s_left = c1.number_input("Hours left to completion", min_value=0)
                    s_planned = c2.number_input("Hours planned for this week", min_value=0)
                    s_comm = st.text_input("Comment")
                    add_task = st.form_submit_button("ADD TO LIST")
                    
                    if add_task:
                        if s_date.weekday() != 6: # Sunday
                            st.error("Error: Start Date must be a Sunday.")
                        elif e_date.weekday() != 5: # Saturday
                            st.error("Error: End Date must be a Saturday.")
                        elif not s_plan:
                            st.error("Please enter a description.")
                        else:
                            st.session_state.tasks_to_submit.append({
                                "Staff Name": st.session_state.user_name,
                                "Start Date": str(s_date),
                                "End Date": str(e_date),
                                "Work Plan": s_plan,
                                "Hours Left": s_left,
                                "Hours Planned": s_planned,
                                "Comment": s_comm,
                                "Review": "",
                                "Submission Date": str(date.today())
                            })
                            st.success("Task added!")

            if st.session_state.tasks_to_submit:
                st.write("### 📋 Your Pending Tasks")
                pending_df = pd.DataFrame(st.session_state.tasks_to_submit)
                st.dataframe(pending_df)
                if st.button("🚀 SUBMIT ALL TASKS"):
                    current_df = conn.read(worksheet="Tracker", ttl=0)
                    updated_df = pd.concat([current_df, pending_df], ignore_index=True)
                    conn.update(worksheet="Tracker", data=updated_df)
                    st.session_state.tasks_to_submit = []
                    st.success("Submitted successfully!")
                    st.balloons()

        elif choice == "My History":
            st.title("🕒 Your History")
            df = conn.read(worksheet="Tracker", ttl=0)
            my_history = df[df['Staff Name'] == st.session_state.user_name]
            st.dataframe(my_history[::-1], use_container_width=True)

    # 6. REVIEWER INTERFACE
    elif current_view == "Reviewer":
        st.title(f"🔍 Reviewer Dashboard: {st.session_state.user_name}")
        df = conn.read(worksheet="Tracker", ttl=0)
        assigned_staff = reviewer_mapping.get(st.session_state.user_name, [])
        
        # Base filter for assigned staff
        reviewer_df = df[df['Staff Name'].isin(assigned_staff)]
        
        if not reviewer_df.empty:
            # 6a. FILTER SECTION FOR REVIEWER
            st.subheader("Filters")
            col_rev1, col_rev2 = st.columns(2)
            
            # Reviewer can only filter within their assigned staff list
            rev_name_filter = col_rev1.selectbox("Filter Assigned Staff", ["All"] + sorted(list(set(reviewer_df["Staff Name"]))))
            rev_date_range = col_rev2.date_input("Filter by Period (Reviewer)", value=[])

            filtered_rev_df = reviewer_df.copy()
            
            if rev_name_filter != "All":
                filtered_rev_df = filtered_rev_df[filtered_rev_df["Staff Name"] == rev_name_filter]
            
            if len(rev_date_range) == 2:
                filtered_rev_df = filtered_rev_df[
                    (pd.to_datetime(filtered_rev_df['Start Date']).dt.date >= rev_date_range[0]) & 
                    (pd.to_datetime(filtered_rev_df['Start Date']).dt.date <= rev_date_range[1])
                ]

            st.write("---")
            
            # 6b. COMMENT SECTION
            if not filtered_rev_df.empty:
                st.subheader("Add/Update Review")
                selected_row_idx = st.selectbox("Select a submission to comment on", filtered_rev_df.index)
                selected_data = filtered_rev_df.loc[selected_row_idx]
                
                st.info(f"Commenting on: **{selected_data['Staff Name']}** | Task: {selected_data['Work Plan'][:60]}...")
                
                with st.form("review_form"):
                    review_comment = st.text_area("Reviewer Comment", value=str(selected_data.get('Review', "")))
                    submit_review = st.form_submit_button("SAVE COMMENT")
                    
                    if submit_review:
                        # We update the original master 'df' using the index
                        df.at[selected_row_idx, 'Review'] = review_comment
                        conn.update(worksheet="Tracker", data=df)
                        st.success("Comment saved successfully!")
                        st.rerun()
                
                st.write("### Assigned Tasks View")
                st.dataframe(filtered_rev_df, use_container_width=True)
            else:
                st.warning("No records found matching these filters.")
        else:
            st.info("No submissions found for your assigned staff yet.")

    # 7. ADMIN INTERFACE
    elif current_view == "Admin":
        st.title("👨‍💼 Admin Master Dashboard")
        df = conn.read(worksheet="Tracker", ttl=0)
        if not df.empty:
            st.subheader("Filters")
            col_f1, col_f2 = st.columns(2)
            name_filter = col_f1.selectbox("Filter by Name", ["All"] + sorted(df["Staff Name"].unique().tolist()))
            date_range = col_f2.date_input("Filter by Period", value=[])

            filtered_df = df.copy()
            if name_filter != "All":
                filtered_df = filtered_df[filtered_df["Staff Name"] == name_filter]
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['Start Date']).dt.date >= date_range[0]) & 
                    (pd.to_datetime(filtered_df['Start Date']).dt.date <= date_range[1])
                ]
            
            st.dataframe(filtered_df, use_container_width=True)
