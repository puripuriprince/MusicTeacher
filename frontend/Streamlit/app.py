import streamlit as st

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login Form (displayed only when not logged in)
if not st.session_state.logged_in:
    st.title("MusicTeacher Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Simulate login success (no actual authentication)
        st.session_state.logged_in = True
        st.rerun()

# Main Application (displayed after login)
else:
    pages = [
        st.Page("page/welcome.py", title="Welcome", icon="👋"),
        st.Page("page/ua.py", title="Upload & Analyze", icon="📷"),
        st.Page("page/practice.py", title="Personalized Practice", icon="🎻"),
        st.Page("page/progress.py", title="Progress Tracker", icon="📈")
    ]

    # Configure sidebar navigation
    with st.sidebar:
        # App branding (can replace with an image later)
        st.title("MusicTeacher")
        selected_page = st.navigation(pages)

    # Run the selected page
    selected_page.run()