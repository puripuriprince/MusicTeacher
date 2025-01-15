import streamlit as st
import os
import tempfile
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_page():
    st.title("Practice Songs")

    # Store the current audio path in session state
    if "current_audio_path" not in st.session_state:
        st.session_state.current_audio_path = None

    # Get user preferences
    col1, col2, col3 = st.columns(3)
    with col1:
        skill_level = st.selectbox(
            "Skill Level:", ["Beginner", "Intermediate", "Advanced"]
        )
    with col2:
        instrument = st.selectbox("Instrument:", ["Piano", "Guitar", "Violin"])
    with col3:
        style = st.selectbox("Style:", ["Classical", "Jazz", "Pop"])

    if st.button("Generate Practice Song"):
        # Clean up previous audio file if it exists
        if (
            st.session_state.current_audio_path
            and os.path.exists(st.session_state.current_audio_path)
        ):
            try:
                os.unlink(st.session_state.current_audio_path)
            except Exception as e:
                print(f"Error cleaning up previous audio: {e}")

        with st.spinner("Generating your practice song..."):
            try:
                base_url = os.getenv("API_BASE_URL")
                response = requests.post(
                    f"{base_url}/api/generate-practice-song",
                    json={
                        "skill_level": skill_level.lower(),
                        "instrument": instrument,
                        "style": style,
                    },
                )
                response.raise_for_status()  # Check for HTTP errors
                song_data = response.json()

                if song_data.get("sheet_music", {}).get("audio_data"):
                    # Create temporary files for the media
                    audio_data = base64.b64decode(
                        song_data["sheet_music"]["audio_data"]
                    )
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                        f.write(audio_data)
                        audio_path = f.name

                    # Store the new audio path
                    st.session_state.current_audio_path = audio_path

                    # Display the audio file
                    st.audio(audio_path)

                    # Display exercise instructions
                    st.subheader("Practice Instructions")
                    for exercise in song_data.get("exercises", []):
                        st.write(exercise)

                    st.subheader("Additional Notes")
                    st.write(song_data.get("notes", ""))

                    if "sheet_music" in song_data:
                        if "sheet_music_path" in song_data["sheet_music"]:
                            sheet_music_path = song_data["sheet_music"][
                                "sheet_music_path"
                            ]
                            if os.path.exists(sheet_music_path):
                                st.image(sheet_music_path, caption="Sheet Music")
                            else:
                                st.error(
                                    f"Sheet music file not found at {sheet_music_path}"
                                )
                        else:
                            st.error("Sheet music path not provided in the response.")
                    else:
                        st.error("No sheet music data found in the response.")
                else:
                    st.error("Failed to generate audio. Please try again.")

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred during the API request: {e}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.button("Generate Test Sheet Music"):
        with st.spinner("Generating test sheet music..."):
            try:
                base_url = os.getenv("API_BASE_URL")
                response = requests.get(f"{base_url}/api/test-sheet-music")
                response.raise_for_status()  # Check for HTTP errors

                result = response.json()
                if "sheet_music" in result:
                    # Display audio
                    if "audio_data" in result["sheet_music"]:
                        audio_data = base64.b64decode(result["sheet_music"]["audio_data"])
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                            f.write(audio_data)
                            st.audio(f.name)

                    # Display PDF
                    if "sheet_music_path" in result["sheet_music"]:
                        sheet_music_path = result["sheet_music"]["sheet_music_path"]
                        if os.path.exists(sheet_music_path):
                            with open(sheet_music_path, "rb") as pdf_file:
                                PDFbyte = pdf_file.read()

                                # Add download button
                                st.download_button(
                                    label="Download Sheet Music PDF",
                                    data=PDFbyte,
                                    file_name="sheet_music.pdf",
                                    mime="application/pdf",
                                )

                                # Base64 encode PDF for display
                                base64_pdf = base64.b64encode(PDFbyte).decode("utf-8")
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        else:
                            st.error(f"Sheet music file not found at {sheet_music_path}")
                    else:
                        st.error("Sheet music path not provided in the response.")
                else:
                    st.error("No sheet music data found in the response.")

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred during the API request: {e}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__page__":
    show_page()