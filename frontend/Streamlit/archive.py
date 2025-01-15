import streamlit as st
import requests
from PIL import Image
import io
import tempfile
import plotly.graph_objects as go
import numpy as np
import base64
import os
import atexit
from pathlib import Path

# Set up static directory path
STATIC_DIR = Path("static/sheet_music").absolute()
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Set page configuration and custom CSS
st.set_page_config(page_title="Music Learning Assistant", layout="wide")

# Custom CSS for Apple-like styling
st.markdown("""
<style>
    /* Modern typography */
    .main * {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }
    
    /* Clean containers */
    div.stButton > button {
        background-color: #FF6B6B;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 20px;
        font-weight: 500;
    }
    
    div.stButton > button:hover {
        background-color: #FF8787;
    }
    
    /* Progress bar styling */
    div.stProgress > div > div {
        background-color: #4ECDC4;
        border-radius: 10px;
    }
    
    /* Card styling */
    .apple-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
    }
    
    /* Section headers */
    .section-header {
        font-size: 24px;
        font-weight: 500;
        margin-bottom: 1.5rem;
        color: #2C3E50;
    }
    
    /* Feedback text */
    .feedback-text {
        color: #34495E;
        line-height: 1.5;
        font-size: 16px;
    }
    
    /* Dividers */
    .subtle-divider {
        border-top: 1px solid #ECF0F1;
        margin: 1rem 0;
    }
    
    /* Score display */
    .score-display {
        font-size: 28px;
        font-weight: 500;
        color: #4ECDC4;
    }

    /* Streamlit native elements override */
    .stRadio > label {
        color: #2C3E50;
    }

    .stSlider > label {
        color: #2C3E50;
    }

    .stSelectbox > label {
        color: #2C3E50;
    }
    
    .feedback-block {
        margin: 1.5rem 0;
        padding: 0.5rem 1rem;
        background: #f8f9fa;
        border-radius: 12px;
    }
    
    .aspect-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .aspect-title {
        color: white;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .grade {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 0.2rem 0.8rem;
    }
    
    .feedback-points {
        color: #cccccc;
    }
    
    .feedback-points p {
        margin: 0.3rem 0;
    }

    .grade-summary {
        background: #1a1a1a;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .grade-summary h2 {
        color: white;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        text-align: center;
    }
    
    .grade-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
    }
    
    .grade-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1rem;
        background: #242424;
        border-radius: 10px;
    }
    
    .grade-label {
        color: #ffffff;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .grade-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .overall {
        background: #2d2d2d;
        border: 1px solid #333;
    }
    
    .grade-value.ultra {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;  /* Bigger than normal grades */
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);  /* Golden glow */
        animation: ultra-pulse 2s infinite;
    }
    
    @keyframes ultra-pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("Music Learning Assistant", anchor=False)
    
    # Sidebar for navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "",
            ["Upload Performance", "Practice Songs", "Progress Tracker"],
            label_visibility="collapsed"
        )
    
    if page == "Upload Performance":
        show_upload_page()
    elif page == "Practice Songs":
        show_practice_songs_page()
    elif page == "Progress Tracker":
        show_progress_tracker()

def show_upload_page():
    st.markdown("<p class='section-header'>Upload Your Performance</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=['mp4', 'mov'])
    
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            video_path = tmp_file.name
        
        st.video(video_path)
        
        if st.button("Analyze Performance", type="primary"):
            with st.spinner(""):
                files = {'video': uploaded_file}
                response = requests.post('http://localhost:5000/api/analyze-performance', files=files)
                
                if response.status_code == 200:
                    feedback = response.json()
                    
                    # Display Summary Grades
                    col1, col2, col3 = st.columns(3)
                    visual_grade, visual_color = feedback['summary']['visual_grade']
                    audio_grade, audio_color = feedback['summary']['audio_grade']
                    overall_grade, overall_color = feedback['summary']['overall_grade']
                    
                    st.markdown("""
                    <div class='grade-summary'>
                        <h2>Performance Summary</h2>
                        <div class='grade-container'>
                            <div class='grade-section'>
                                <span class='grade-label'>Visual Performance</span>
                                <span class='grade-value' style='color: {visual_color}'>{visual_grade}</span>
                            </div>
                            <div class='grade-section'>
                                <span class='grade-label'>Audio Performance</span>
                                <span class='grade-value' style='color: {audio_color}'>{audio_grade}</span>
                            </div>
                            <div class='grade-section overall'>
                                <span class='grade-label'>Overall Rating</span>
                                <span class='grade-value {ultra_class}' style='color: {overall_color}'>{overall_grade}</span>
                            </div>
                        </div>
                    </div>
                    """.format(
                        visual_grade=visual_grade, visual_color=visual_color,
                        audio_grade=audio_grade, audio_color=audio_color,
                        overall_grade=overall_grade, overall_color=overall_color,
                        ultra_class='ultra' if overall_grade == 'ULTRA' else ''
                    ), unsafe_allow_html=True)
                    
                    if 'performance_summary' in feedback['summary']:
                        st.markdown("""
                        <div style='background: #242424; padding: 1.5rem; border-radius: 15px; margin: 2rem 0;'>
                            <h3 style='color: white; text-align: center; margin-bottom: 1rem;'>Performance Summary</h3>
                            <p style='color: #cccccc; text-align: justify; line-height: 1.6;'>
                                {summary}
                            </p>
                        </div>
                        """.format(summary=feedback['summary']['performance_summary']), unsafe_allow_html=True)
                    
                    # Spider Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        <div style='background: #242424; padding: 1rem; border-radius: 10px;'>
                            <h3 style='color: white; text-align: center; margin-bottom: 1rem;'>Visual Performance Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        visual_chart = create_spider_chart(feedback['visual_feedback'], "Visual Performance")
                        st.plotly_chart(visual_chart, use_container_width=True)
                    
                    with col2:
                        st.markdown("""
                        <div style='background: #242424; padding: 1rem; border-radius: 10px;'>
                            <h3 style='color: white; text-align: center; margin-bottom: 1rem;'>Audio Performance Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        audio_chart = create_spider_chart(feedback['audio_feedback'], "Audio Performance")
                        st.plotly_chart(audio_chart, use_container_width=True)
                    
                    # Remove the Visual Analysis, Audio Analysis, and Practice Tips sections
                    # (Delete or comment out the code that displays these sections)
                else:
                    st.error("Analysis failed. Please try again.")

def show_practice_songs_page():
    st.title("Practice Songs")
    
    # Store the current audio path in session state
    if 'current_audio_path' not in st.session_state:
        st.session_state.current_audio_path = None
    
    # Get user preferences
    col1, col2, col3 = st.columns(3)
    with col1:
        skill_level = st.selectbox("Skill Level:", ["beginner", "intermediate", "advanced"])
    with col2:
        instrument = st.selectbox("Instrument:", ["Piano", "Guitar", "Violin"])
    with col3:
        style = st.selectbox("Style:", ["classical", "jazz", "pop"])
    
    if st.button("Generate Practice Song"):
        # Clean up previous audio file if it exists
        if st.session_state.current_audio_path and os.path.exists(st.session_state.current_audio_path):
            try:
                os.unlink(st.session_state.current_audio_path)
            except Exception as e:
                print(f"Error cleaning up previous audio: {e}")
        
        with st.spinner("Generating your practice song..."):
            try:
                response = requests.post(
                    'http://localhost:5000/api/generate-practice-song',
                    json={
                        'skill_level': skill_level.lower(),
                        'instrument': instrument,
                        'style': style
                    }
                )
                
                if response.status_code == 200:
                    song_data = response.json()
                    
                    if song_data.get('sheet_music', {}).get('audio_data'):
                        # Create temporary files for the media
                        audio_data = base64.b64decode(song_data['sheet_music']['audio_data'])
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                            f.write(audio_data)
                            audio_path = f.name
                        
                        # Store the new audio path
                        st.session_state.current_audio_path = audio_path
                        
                        # Display the audio file
                        st.audio(audio_path)
                        
                        # Display exercise instructions
                        st.subheader("Practice Instructions")
                        for exercise in song_data.get('exercises', []):
                            st.write(exercise)
                        
                        st.subheader("Additional Notes")
                        st.write(song_data.get('notes', ''))
                        
                        if 'sheet_music' in song_data:
                            if 'sheet_music_path' in song_data['sheet_music']:
                                sheet_music_path = song_data['sheet_music']['sheet_music_path']
                                if os.path.exists(sheet_music_path):
                                    st.image(sheet_music_path, caption="Sheet Music")
                                else:
                                    st.error(f"Sheet music file not found at {sheet_music_path}")
                    else:
                        st.error("Failed to generate audio. Please try again.")
                else:
                    st.error("Failed to generate practice song. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.button("Generate Test Sheet Music"):
        with st.spinner("Generating test sheet music..."):
            try:
                response = requests.get('http://localhost:5000/api/test-sheet-music')
                
                if response.status_code == 200:
                    result = response.json()
                    if 'sheet_music' in result:
                        # Display audio
                        if 'audio_data' in result['sheet_music']:
                            audio_data = base64.b64decode(result['sheet_music']['audio_data'])
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                                f.write(audio_data)
                                st.audio(f.name)
                        
                        # Display PDF
                        if 'sheet_music_path' in result['sheet_music']:
                            sheet_music_path = result['sheet_music']['sheet_music_path']
                            if os.path.exists(sheet_music_path):
                                with open(sheet_music_path, "rb") as pdf_file:
                                    PDFbyte = pdf_file.read()
                                    
                                    # Add download button
                                    st.download_button(
                                        label="Download Sheet Music PDF",
                                        data=PDFbyte,
                                        file_name="sheet_music.pdf",
                                        mime='application/pdf'
                                    )
                                    
                                    try:
                                        # Try using the new PDF viewer first
                                        st.pdf_viewer(PDFbyte)
                                    except Exception as e:
                                        # Fallback to base64 encoded iframe
                                        base64_pdf = base64.b64encode(PDFbyte).decode('utf-8')
                                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                                        st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.error(f"Sheet music file not found at {sheet_music_path}")
                else:
                    st.error("Failed to generate test sheet music")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Clean up on session end
def cleanup_audio():
    if hasattr(st.session_state, 'current_audio_path') and st.session_state.current_audio_path:
        try:
            if os.path.exists(st.session_state.current_audio_path):
                os.unlink(st.session_state.current_audio_path)
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup_audio)

def show_progress_tracker():
    st.markdown("<p class='section-header'>Progress Tracker</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class='apple-card'>
        <p class='feedback-text'>Progress tracking features coming soon.</p>
    </div>
    """, unsafe_allow_html=True)

def get_score_color(score):
    if score >= 8.0:
        return "#4ECDC4"  # Teal for high scores
    elif score >= 6.0:
        return "#FFD93D"  # Yellow for medium scores
    else:
        return "#FF6B6B"  # Coral for low scores

def show_aspect_feedback(aspect, data):
    return f"""
    <div class='aspect-container'>
        <div class='aspect-header'>
            <span class='aspect-title'>{aspect.title()}</span>
        </div>
        <div class='feedback-points'>
            {''.join(f"<p>• {point}</p>" for point in data['feedback'])}
        </div>
    </div>
    """

def calculate_overall_rating(feedback):
    all_grades = []
    for data in feedback['visual_feedback'].values():
        all_grades.append(data["style_rating"][0])
    for data in feedback['audio_feedback'].values():
        all_grades.append(data["style_rating"][0])
    
    # Simple grading logic
    if "SSS" in all_grades: return "SSS"
    elif "SS" in all_grades: return "SS"
    elif "S" in all_grades: return "S"
    elif all_grades.count("A") >= 2: return "A"
    elif all_grades.count("B") >= 2: return "B"
    else: return "C"

def get_style_rating(score):
    if score >= 9.5: return ("SSS", "#FF0000")  # Red
    elif score >= 9.0: return ("SS", "#FF0000")  # Red
    elif score >= 8.5: return ("S", "#FF0000")   # Red
    elif score >= 8.0: return ("A", "#FFA500")   # Orange
    elif score >= 7.0: return ("B", "#FFD700")   # Yellow
    elif score >= 6.0: return ("C", "#00FF00")   # Green
    else: return ("D", "#0000FF")                # Blue

# Add this function to create spider charts
def create_spider_chart(feedback_data, title):
    """Create spider chart using actual scores from feedback data"""
    # Skip the overall score and only use individual aspects
    categories = []
    scores = []
    
    # Extract scores from feedback data
    for k, v in feedback_data.items():
        if k != "score":  # Skip overall score
            categories.append(k.title())
            scores.append(v['score'])  # Use actual score from feedback
    
    # Create the spider chart
    fig = go.Figure()
    
    # Add the data trace
    fig.add_trace(go.Scatterpolar(
        r=scores,  # Using actual scores
        theta=categories,
        fill='toself',
        fillcolor='rgba(76, 201, 240, 0.3)',  # Light blue with transparency
        line=dict(color='#4CC9F0', width=2),
        name=title
    ))
    
    # Update the layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],  # Keep scale from 0 to 10
                showline=False,
                tickfont=dict(color='white'),
            ),
            angularaxis=dict(
                tickfont=dict(color='white', size=12),
                rotation=90,
                direction="clockwise",
            ),
            bgcolor='rgba(0,0,0,0)',  # Transparent background
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        margin=dict(l=80, r=80, t=40, b=40),
        height=400,
    )
    
    return fig

if __name__ == "__main__":
    main()
