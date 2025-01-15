import streamlit as st
import random
import requests
import os
from utils import data_utils, style_utils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_page():
    st.title("Upload & Analyze")

    # Mock upload button
    if st.button("Mock Upload"):
        st.session_state.mock_upload = True
        st.session_state.video_path = "https://www.youtube.com/embed/tz56ac6BaJQ"
        st.session_state.feedback_data = data_utils.generate_mock_feedback()

    # File uploader (only shown if not a mock upload)
    if not st.session_state.get("mock_upload", False):
        uploaded_file = st.file_uploader("", type=["mp4", "mov"])
        if uploaded_file is not None:
            st.session_state.video_path = uploaded_file
            # Analyze the performance using the API
            with st.spinner("Analyzing performance..."):
                base_url = os.getenv("API_BASE_URL")
                url = f"{base_url}/api/analyze-performance"
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
            visual_grade, visual_color = style_utils.get_style_rating(
                st.session_state.feedback_data["summary"]["visual_grade"][0]
            )
            st.markdown(
                style_utils.style_grade_container("Visual", visual_grade, visual_color),
                unsafe_allow_html=True,
            )
        with col2:
            audio_grade, audio_color = style_utils.get_style_rating(
                st.session_state.feedback_data["summary"]["audio_grade"][0]
            )
            st.markdown(
                style_utils.style_grade_container("Audio", audio_grade, audio_color),
                unsafe_allow_html=True,
            )
        with col3:
            overall_grade, overall_color = style_utils.get_style_rating(
                st.session_state.feedback_data["summary"]["overall_grade"][0]
            )
            st.markdown(
                style_utils.style_grade_container(
                    "Overall", overall_grade, overall_color, is_overall=True
                ),
                unsafe_allow_html=True,
            )

        # Performance summary text
        st.markdown(
            style_utils.style_summary_container(
                st.session_state.feedback_data["summary"]["performance_summary"]
            ),
            unsafe_allow_html=True,
        )

        # Spider Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                style_utils.style_spider_chart_container("Visual Performance Analysis"),
                unsafe_allow_html=True,
            )
            visual_chart = data_utils.create_spider_chart(
                st.session_state.feedback_data["visual_feedback"],
                "Visual Performance",
            )
            st.plotly_chart(visual_chart, use_container_width=True)

        with col2:
            st.markdown(
                style_utils.style_spider_chart_container("Audio Performance Analysis"),
                unsafe_allow_html=True,
            )
            audio_chart = data_utils.create_spider_chart(
                st.session_state.feedback_data["audio_feedback"], "Audio Performance"
            )
            st.plotly_chart(audio_chart, use_container_width=True)

        # Score Editing Form
        with st.expander("Score Editing"):
            with st.form("score_form"):
                st.subheader("Edit Scores")
                edited_scores = {}
                for category, data in st.session_state.feedback_data.items():
                    if isinstance(data, dict):
                        edited_scores[category] = {}
                        for aspect, aspect_data in data.items():
                            if aspect != "score":
                                edited_scores[category][aspect] = st.number_input(
                                    f"{category.title()} - {aspect.title()}",
                                    min_value=0.0,
                                    max_value=10.0,
                                    value=float(aspect_data["score"]),
                                    step=0.1,
                                )

                if st.form_submit_button("Update Scores"):
                    # Update the feedback_data with edited scores
                    for category, aspects in edited_scores.items():
                        for aspect, score in aspects.items():
                            st.session_state.feedback_data[category][aspect][
                                "score"
                            ] = score

                    # Recalculate overall scores and grades
                    st.session_state.feedback_data["summary"][
                        "visual_grade"
                    ] = style_utils.get_style_rating(
                        sum(
                            st.session_state.feedback_data["visual_feedback"][aspect][
                                "score"
                            ]
                            for aspect in st.session_state.feedback_data["visual_feedback"]
                            if aspect != "score"
                        )
                        / (len(st.session_state.feedback_data["visual_feedback"]) - 1)
                    )
                    st.session_state.feedback_data["summary"][
                        "audio_grade"
                    ] = style_utils.get_style_rating(
                        sum(
                            st.session_state.feedback_data["audio_feedback"][aspect][
                                "score"
                            ]
                            for aspect in st.session_state.feedback_data["audio_feedback"]
                            if aspect != "score"
                        )
                        / (len(st.session_state.feedback_data["audio_feedback"]) - 1)
                    )
                    st.session_state.feedback_data["summary"][
                        "overall_grade"
                    ] = style_utils.get_style_rating(
                        (
                            st.session_state.feedback_data["summary"]["visual_grade"][
                                0
                            ]
                            + st.session_state.feedback_data["summary"]["audio_grade"][
                                0
                            ]
                        )
                        / 2
                    )

                    st.rerun()

    # Instrument Picker (could also be in the sidebar)
    instrument = st.selectbox(
        "Instrument:", ["Ukulele", "Others (Under Construction)"]
    )

if __name__ == "__page__":
    show_page()