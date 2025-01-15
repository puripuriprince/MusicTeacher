

import streamlit as st
import plotly.graph_objects as go
from utils import data_utils

def show_page():
    st.title("Progress Tracker")

    # Mock User Profile
    st.subheader("User Profile")
    st.write("Name: John Doe")  # Example
    st.write("Instrument: Ukulele")
    st.write("Level: Intermediate")

    # Progress Timeline
    st.subheader("Progress Timeline")
    mock_data = data_utils.generate_mock_progress_data()

    # Create Plotly chart
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=mock_data["Date"], y=mock_data["Score"], mode="lines+markers", name="Score")
    )
    fig.update_layout(
        title="Performance Over Time",
        xaxis_title="Date",
        yaxis_title="Score",
        yaxis=dict(range=[0, 10]),
    )

    st.plotly_chart(fig)

    # Achievements
    st.subheader("Achievements")
    achievements = data_utils.generate_mock_achievements(mock_data)
    for achievement in achievements:
        st.write(f"- {achievement}")

if __name__ == "__page__":
    show_page()