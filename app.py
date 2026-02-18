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

    # ENTER BUTTON
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
    # LOGOUT BUTTON
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    
    # TOGGLE OPTION FOR ADMIN
    if st.session_state.role == "Admin":
        admin_mode = st.sidebar.toggle("Switch to User View", value=False)
        current_view = "User" if admin_mode else "Admin"
    else:
        current_view = "User"

    # 5. USER INTERFACE
    if current_view == "User":
        display_name = st.session_state.user_name if st.session_state.user_name else "Admin (Testing)"
        st.sidebar.info(f"Viewing as: {display_name}")
        
        choice = st.sidebar.radio("Menu", ["Submit Work Plan", "My History"])

        if choice == "Submit Work Plan":
            st.title("📝 New Work Plan")
            with st.form("user_form"):
                st.write(f"Staff: **{display_name}**")
                
                # DATE LOCKED TO TODAY
                s_date = st.date_input("Date", date.today(), disabled=True)
                
                s_plan = st.text_area("Work Plan Details")
                c1, c2 = st.columns(2)
                s_left = c1.number_input("Hours left to completion", min_value=0)
                s_planned = c2.number_input("Hours planned for this week", min_value=0)
                s_comm = st.text_input("Comment")
                
                confirm = st.checkbox("Confirm details")
                submit_btn = st.form_submit_button("SUBMIT PLAN")

                if submit_btn and confirm:
                    new_entry = pd.DataFrame([{
                        "Staff Name": display_name,
                        "Date": str(s_date), 
                        "Work Plan": s_plan,
                        "Hours left to completion": s_left, 
                        "Hours planned for this week": s_planned,
                        "Comment": s_comm
                    }])
                    current_df = conn.read(worksheet="Tracker", ttl=0)
                    updated_df = pd.concat([current_df, new_entry], ignore_index=True)
                    conn.update(worksheet="Tracker", data=updated_df)
                    st.success("Submitted successfully!")
                    st.balloons()

        elif choice == "My History":
            st.title("🕒 Your History")
            my_history = conn.read(worksheet="Tracker", ttl=0)
            my_history = my_history[my_history['Staff Name'] == display_name]
            st.table(my_history[::-1])

    # 6. ADMIN INTERFACE
    elif current_view == "Admin":
        st.title("👨‍💼 Admin Master Dashboard")
        df = conn.read(worksheet="Tracker", ttl=0)
        
        if not df.empty:
            if 'Status' in df.columns:
                df = df.drop(columns=['Status'])

            st.subheader("Filters")
            col_f1, col_f2 = st.columns(2)
            
            # Name Filter
            unique_names = ["All"] + sorted(df["Staff Name"].unique().tolist())
            name_filter = col_f1.selectbox("Filter by Name", unique_names)
            
            # Date Filter
            date_filter = col_f2.date_input("Filter by Date", value=None)

            filtered_df = df.copy()
            if name_filter != "All":
                filtered_df = filtered_df[filtered_df["Staff Name"] == name_filter]
            
            if date_filter:
                filtered_df = filtered_df[filtered_df["Date"] == str(date_filter)]
            
            st.write("---")
            st.write(f"Showing **{len(filtered_df)}** records")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No data found in the Tracker.")
