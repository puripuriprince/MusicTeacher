import random
import pandas as pd
import plotly.graph_objects as go

def generate_mock_feedback():
    """Generates mock feedback data for the mock upload."""
    feedback_data = {
        "visual_feedback": {
            "posture": {
                "score": random.uniform(7, 9),
                "feedback": ["Good posture overall.", "Keep your back straight."],
                "style_rating": ["A", "#FFA500"],
            },
            "finger_position": {
                "score": random.uniform(6, 8),
                "feedback": ["Accurate finger placement.", "Practice more on string 3."],
                "style_rating": ["B", "#FFD700"],
            },
            "confidence": {
                "score": random.uniform(8, 10),
                "feedback": ["Confident performance.", "Maintain eye contact."],
                "style_rating": ["S", "#FF0000"],
            },
        },
        "audio_feedback": {
            "tempo": {
                "score": random.uniform(7, 9),
                "feedback": ["Tempo is consistent.", "Try to speed up slightly."],
                "style_rating": ["SS", "#FF0000"],
            },
            "pitch": {
                "score": random.uniform(5, 7),
                "feedback": ["Pitch is accurate.", "Work on intonation."],
                "style_rating": ["C", "#00FF00"],
            },
            "rhythm": {
                "score": random.uniform(4, 6),
                "feedback": ["Good rhythmic sense.", "Focus on syncopation."],
                "style_rating": ["D", "#0000FF"],
            },
        },
        "education_tips": {
            "immediate_focus": ["Work on finger transitions."],
            "technical_development": ["Practice scales and arpeggios."],
            "performance_growth": ["Focus on dynamics and expression."],
        },
        "summary": {
            "visual_grade": ["A", "#FFA500"],
            "audio_grade": ["B", "#FFD700"],
            "overall_grade": ["B", "#FFD700"],
            "performance_summary": "A solid performance with areas for improvement.",
        },
    }
    return feedback_data

def generate_mock_progress_data(num_days=30):
    """Generates mock progress data for the Progress Tracker."""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=num_days)
    scores = [random.randint(4, 10) for _ in range(num_days)]
    practice_hours = [random.uniform(0.5, 3) for _ in range(num_days)]
    return pd.DataFrame({"Date": dates, "Score": scores, "Practice Hours": practice_hours})

def generate_mock_achievements(mock_data):
    """Generates mock achievements based on the mock progress data."""
    achievements = []
    if mock_data["Score"].max() >= 9:
        achievements.append("Achieved a score of 9 or higher!")
    if mock_data["Practice Hours"].sum() >= 20:
        achievements.append("Practiced for a total of 20 hours or more!")
    if (mock_data["Score"] >= 7).all():
        achievements.append("Maintained a score of 7 or higher consistently!")
    return achievements

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