import streamlit as st

def apply_custom_css():
    """Applies custom CSS based on dark mode state."""
    if st.session_state.dark_mode:
        st.markdown(
            """
            <style>
                /* General text color */
                body, .main * {
                    color: #f5f5f5;
                }
                /* Sidebar background */
                .css-1d391kg {
                    background-color: #262730;
                }
                /* Main content area background */
                .main {
                    background-color: #121212;
                }
                /* File uploader and text input colors */
                .stFileUploader, .stTextInput {
                    color: #f5f5f5;
                }
                /* Button colors */
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
                /* Radio button colors */
                .st-bx, .st-ec, .st-el, .st-cn, .st-cm, .st-cl, .st-ck, .st-cj, .st-ci, .st-ch, .st-cg, .st-cf, .st-ce, .st-cd, .st-cc, .st-cb, .st-ca, .st-c9, .st-c8, .st-c7, .st-c6, .st-c5, .st-c4, .st-c3, .st-c2, .st-c1, .st-c0, .st-bz, .st-by, .st-bx, .st-bw, .st-bv, .st-bu, .st-bt, .st-bs, .st-br, .st-bq, .st-bp, .st-bo, .st-bn, .st-bm, .st-bl, .st-bk, .st-bj, .st-bi, .st-bh, .st-bg, .st-bf, .st-be, .st-bd, .st-bc, .st-bb, .st-ba, .st-b9, .st-b8, .st-b7, .st-b6, .st-b5, .st-b4, .st-b3, .st-b2, .st-b1, .st-b0, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao, .st-ap, .st-aq, .st-ar, .st-as, .st-at, .st-au, .st-av, .st-aw, .st-ax, .st-ay, .st-az {
                    background-color: #262730 !important;
                    color: #f5f5f5 !important;
                }
                /* Selectbox colors */
                .css-2b097c-container {
                    background-color: #262730;
                    color: #f5f5f5;
                }
                .css-2b097c-container .css-1wa3eu0-placeholder,
                .css-2b097c-container .css-1dimb5e-singleValue {
                    color: #f5f5f5;
                }
                .css-2b097c-container .css-1okebmr-indicatorSeparator {
                    background-color: #f5f5f5;
                }
                /* Checkbox colors */
                .st-bx, .st-bx > div {
                    color: #f5f5f5 !important;
                }
                /* Number input and slider colors */
                .st-de, .st-dn, .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt, .st-du, .st-dv, .st-dw, .st-dx, .st-dy, .st-dz, .st-e0, .st-e1, .st-e2, .st-e3, .st-e4, .st-e5, .st-e6, .st-e7, .st-e8, .st-e9, .st-ea, .st-eb, .st-ec, .st-ed {
                    background-color: #262730 !important;
                    color: #f5f5f5 !important;
                }
                /* Expander colors */
                .css-1s295f8, .css-k7vsy4 {
                    background-color: #262730;
                    color: #f5f5f5;
                }
                .css-k7vsy4 .css-1h9us3y {
                    color: #f5f5f5;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Remove dark mode styles if disabled
        st.markdown(
            """
            <style>
                /* Remove dark mode styles here if needed */
            </style>
            """,
            unsafe_allow_html=True,
        )

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

def style_grade_container(label, grade, color, is_overall=False):
    """Styles the grade container with the given label, grade, and color."""
    if is_overall:
        return f"""
        <div class='grade-section overall'>
            <span class='grade-label'>{label}</span>
            <span class='grade-value' style='color: {color}; font-size: larger;'>{grade}</span>
        </div>
        """
    else:
        return f"""
        <div class='grade-section'>
            <span class='grade-label'>{label}</span>
            <span class='grade-value' style='color: {color}'>{grade}</span>
        </div>
        """

def style_summary_container(summary):
    """Styles the performance summary container."""
    return f"""
    <div style='background: #242424; padding: 1.5rem; border-radius: 15px; margin: 2rem 0;'>
        <h3 style='color: white; text-align: center; margin-bottom: 1rem;'>Performance Summary</h3>
        <p style='color: #cccccc; text-align: justify; line-height: 1.6;'>
            {summary}
        </p>
    </div>
    """

def style_spider_chart_container(title):
    """Styles the spider chart container."""
    return f"""
    <div style='background: #242424; padding: 1rem; border-radius: 10px;'>
        <h3 style='color: white; text-align: center; margin-bottom: 1rem;'>{title}</h3>
    </div>
    """