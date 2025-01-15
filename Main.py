import streamlit as st
import requests
from PIL import Image
import io
import tempfile
import plotly.graph_objects as go
import numpy as np

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
                    
                    # Visual Analysis
                    st.markdown("""
                    <div class='feedback-section'>
                        <div class='section-title'>
                            <span>Visual Analysis</span>
                            <div class='section-line'></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for aspect, data in feedback['visual_feedback'].items():
                        if aspect != "score":  # Skip the overall score
                            st.markdown(show_aspect_feedback(aspect, data), unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Audio Analysis (similar structure)
                    st.markdown("""
                    <div class='feedback-section'>
                        <div class='section-title'>
                            <span>Audio Analysis</span>
                            <div class='section-line'></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for aspect, data in feedback['audio_feedback'].items():
                        if aspect != "score":  # Skip the overall score
                            st.markdown(show_aspect_feedback(aspect, data), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Practice Tips
                    st.markdown("""
                    <div class='feedback-section tips-section'>
                        <div class='section-title'>
                            <span>Practice Focus</span>
                            <div class='section-line'></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for category, tips in feedback['education_tips'].items():
                        st.markdown(f"""
                        <div class='tips-category'>
                            <h4>{category.replace('_', ' ').title()}</h4>
                            <div class='tips-list'>
                                {''.join(f"<p>• {tip}</p>" for tip in tips)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else:
                    st.error("Analysis failed. Please try again.")

def show_practice_songs_page():
    st.markdown("<p class='section-header'>Generate Practice Songs</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        instrument = st.selectbox("Instrument", ["Ukulele", "Guitar", "Piano", "Violin"], label_visibility="collapsed")
    with col2:
        skill_level = st.slider("Skill Level", 1, 10, 5, label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("Generate", use_container_width=True):
            with st.spinner(""):
                response = requests.post('http://localhost:5000/api/generate-practice-song', 
                                      json={'skill_level': skill_level, 'instrument': instrument})
                
                if response.status_code == 200:
                    song_data = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.audio(song_data['song_url'])
                    with col2:
                        st.image(song_data['sheet_music'])
                else:
                    st.error("Generation failed. Please try again.")
    st.markdown("</div>", unsafe_allow_html=True)

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
    # Skip the overall score and only use individual aspects
    categories = [k.title() for k in feedback_data.keys() if k != "score"]
    
    # Create scores array (we'll use fixed scores for visual representation)
    scores = [10, 8, 9]  # Example scores for each aspect
    
    # Create the spider chart
    fig = go.Figure()
    
    # Add the data trace
    fig.add_trace(go.Scatterpolar(
        r=scores,
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
                range=[0, 10],
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
