import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock feedback data (constant)
MOCK_FEEDBACK_DATA = {
    "visual_feedback": {
        "score": 7.8,
        "posture": {
            "score": 8.5,
            "feedback": [
                "Shoulders and back alignment are excellent.",
                "Slight tension noticed in neck position.",
                "Good eye level with the instrument."
            ],
            "style_rating": ("S", "#FF0000")
        },
        "finger_position": {
            "score": 9.2,
            "feedback": [
                "Clean chord transitions in most sections.",
                "Some hesitation in complex finger patterns.",
                "Right hand strumming is consistent."
            ],
            "style_rating": ("SS", "#FF0000")
        },
        "confidence": {
            "score": 7.8,
            "feedback": [
                "Natural stage presence developing well.",
                "Performance becomes hesitant in difficult passages.",
                "Good recovery from minor mistakes."
            ],
            "style_rating": ("B", "#FFD700")
        }
    },
    "audio_feedback": {
        "score": 8.1,
        "tempo": {
            "score": 8.8,
            "feedback": [
                "Steady rhythm in main sections.",
                "Slight rushing in chorus transitions.",
                "Good use of dynamic pacing."
            ],
            "style_rating": ("S", "#FF0000")
        },
        "pitch": {
            "score": 7.5,
            "feedback": [
                "Excellent intonation in middle register.",
                "Minor pitch variations in higher notes.",
                "Strong sense of key maintenance."
            ],
            "style_rating": ("B", "#FFD700")
        },
        "rhythm": {
            "score": 9.5,
            "feedback": [
                "Consistent strumming patterns.",
                "Complex rhythms handled well.",
                "Some syncopation needs attention."
            ],
            "style_rating": ("SSS", "#FF0000")
        }
    },
    "education_tips": {
        "immediate_focus": [
            "Practice difficult transitions at 70 percent speed.",
            "Record yourself to analyze neck tension points."
        ],
        "technical_development": [
            "Incorporate finger exercises for complex patterns.",
            "Use a metronome for chorus transition sections."
        ],
        "performance_growth": [
            "Try performing the difficult sections for friends.",
            "Practice recovery techniques for common mistakes."
        ]
    },
    "summary": {
        "visual_grade": ("B", "#FFD700"),
        "audio_grade": ("A", "#FFA500"),
        "overall_grade": ("B", "#FFD700"),
        "performance_summary": "The performance demonstrates a good grasp of fundamental techniques with areas for improvement in complex passages. Visual presentation is engaging, and audio quality is generally consistent. Further development in technical skills and performance confidence is recommended."
    }
}

# Function to get style rating (replace with your actual implementation if different)
def get_style_rating(score):
    if score >= 9.5:
        return ("SSS", "#FF0000")  # Red
    elif score >= 9.0:
        return ("SS", "#FF0000")  # Red
    elif score >= 8.5:
        return ("S", "#FF0000")  # Red
    elif score >= 8.0:
        return ("A", "#FFA500")  # Orange
    elif score >= 7.0:
        return ("B", "#FFD700")  # Yellow
    elif score >= 6.0:
        return ("C", "#00FF00")  # Green
    else:
        return ("D", "#0000FF")  # Blue

# Function to create spider chart (replace with your actual implementation)
def create_spider_chart(data, title):
    import plotly.graph_objects as go

    categories = list(data.keys())
    categories.remove("score")
    values = [data[category]["score"] for category in categories]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(r=values, theta=categories, fill="toself", name=title)
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False
    )

    return fig

def show_page():
    st.title("Upload & Analyze")

    # Mock upload button
    if st.button("Mock Upload"):
        st.session_state.mock_upload = True
        st.session_state.video_path = "https://www.youtube.com/embed/tz56ac6BaJQ"
        st.session_state.feedback_data = MOCK_FEEDBACK_DATA

    # File uploader (only shown if not a mock upload)
    if not st.session_state.get("mock_upload", False):
        uploaded_file = st.file_uploader("", type=["mp4", "mov"])
        if uploaded_file is not None:
            st.session_state.video_path = uploaded_file
            # Analyze the performance using the API
            with st.spinner("Analyzing performance..."):
                base_url = os.getenv("API_BASE_URL")
                url = f"{base_url}/api/analyze-performance"  # Use the base_url variable here
                files = {"video": uploaded_file}

                try:
                    response = requests.post(url, files=files)
                    response.raise_for_status()
                    st.session_state.feedback_data = response.json()
                except requests.exceptions.RequestException as e:
                    st.error(f"Error during API request: {e}")
                    st.session_state.feedback_data = None

    # Video Player
    if "video_path" in st.session_state:
        st.video(st.session_state.video_path)

    # Display feedback data if available
    if "feedback_data" in st.session_state and st.session_state.feedback_data is not None:
        # Summary Grades
        col1, col2, col3 = st.columns(3)
        with col1:
            visual_score = st.session_state.feedback_data["visual_feedback"]["score"]
            visual_grade, visual_color = st.session_state.feedback_data["summary"]["visual_grade"]
            st.markdown(
                f"<div style='text-align: center; padding: 10px; border-radius: 10px; background-color: {visual_color}; color: white; font-size: 20px;'><span style='font-size: 24px;'>Visual:</span> <br/> {visual_grade}</div>",
                unsafe_allow_html=True,
            )
        with col2:
            audio_score = st.session_state.feedback_data["audio_feedback"]["score"]
            audio_grade, audio_color = st.session_state.feedback_data["summary"]["audio_grade"]
            st.markdown(
                f"<div style='text-align: center; padding: 10px; border-radius: 10px; background-color: {audio_color}; color: white; font-size: 20px;'><span style='font-size: 24px;'>Audio:</span> <br/> {audio_grade}</div>",
                unsafe_allow_html=True,
            )
        with col3:
            overall_score = (visual_score + audio_score) / 2
            overall_grade, overall_color = st.session_state.feedback_data["summary"]["overall_grade"]
            st.markdown(
                f"<div style='text-align: center; padding: 10px; border-radius: 10px; background-color: {overall_color}; color: white; font-size: 20px;'><span style='font-size: 24px;'>Overall:</span> <br/> {overall_grade}</div>",
                unsafe_allow_html=True,
            )

        # Performance summary text
        st.markdown(
            f"<div style='padding: 10px; border-radius: 10px; border: 1px solid #e6e6e6; margin-top: 20px;'>{st.session_state.feedback_data['summary']['performance_summary']}</div>",
            unsafe_allow_html=True,
        )

        # Spider Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "<div style='text-align: center; font-size: 20px; margin-top: 20px;'>Visual Performance Analysis</div>",
                unsafe_allow_html=True,
            )
            visual_chart = create_spider_chart(
                st.session_state.feedback_data["visual_feedback"],
                "Visual Performance",
            )
            st.plotly_chart(visual_chart, use_container_width=True)

        with col2:
            st.markdown(
                "<div style='text-align: center; font-size: 20px; margin-top: 20px;'>Audio Performance Analysis</div>",
                unsafe_allow_html=True,
            )
            audio_chart = create_spider_chart(
                st.session_state.feedback_data["audio_feedback"], "Audio Performance"
            )
            st.plotly_chart(audio_chart, use_container_width=True)

    # Instrument Picker
    instrument = st.selectbox(
        "Instrument:", ["Ukulele", "Others (Under Construction)"]
    )

if __name__ == "__page__":
    show_page()