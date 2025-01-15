import streamlit as st
from utils import style_utils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state (only dark mode needed for the homepage)
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def show_homepage():
    """Displays the homepage content."""

    st.title("🎵 MusicTeacher")

    st.write(
        """
        Welcome to MusicTeacher, your AI-powered music learning companion! 
        This app uses a vision model, sound analysis, and a Large Language Model (LLM) to help you improve your musical skills. 
        We focus on enhancing your style, tempo, confidence, and even creative writing abilities related to music.
        """
    )

    st.subheader("✨ Features")
    st.markdown(
        """
        - **Upload & Analyze:** Upload a video of you playing an instrument (e.g., ukulele). 
          Our app uses computer vision and sound analysis to provide feedback on your technique.
        - **Practice Songs:** We generate practice songs tailored to your skill level and instrument, along with sheet music and additional notes.
        - **Progress Tracker:** Track your improvement over time with scores and visualizations. (Coming soon!)
        """
    )

    st.subheader("🛠️ Technologies Used")
    st.markdown(
        """
        - **Frontend:** Streamlit (a modern alternative to React for rapid prototyping and data apps)
        - **Vision:** [Nebius AI](https://nebius.com/) (replace with the actual link if available)
        - **Education Advice:** [OpenNote](https://opennote.io/) (replace with the actual link if available) (LLM for educational content)
        - **Music Generation:** [Beethoven.ai](beethoven.ai) (replace with the actual link if available)
        - **Database & Users:** [Supabase](https://supabase.com/) (replace with the actual link if available)
        """
    )

    st.subheader("🚀 How to Use")
    st.write(
        """
        1. **Upload a video** of yourself playing your instrument.
        2. **Get feedback** on your performance (style, tempo, etc.).
        3. **Generate a practice song** and play it.
        4. **Upload a new video** of your practice for more feedback.
        """
    )

def show_page():
    # Apply custom CSS for dark mode (if enabled)
    style_utils.apply_custom_css()

    # Sidebar for dark mode toggle
    with st.sidebar:
        st.session_state.dark_mode = st.checkbox("🌙 Dark Mode")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Show the homepage content
    show_homepage()
    
if __name__ == "__page__":
    show_page()