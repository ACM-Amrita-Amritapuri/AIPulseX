import base64
import tempfile
from gtts import gTTS
import streamlit as st


def Output_Speech(text):
    """
    Converts the given text to speech and plays it using Streamlit.

    Parameters:
    - text (str): The text to be converted to speech.
    """
    if text:
        try:
            # Convert text to speech
            tts = gTTS(text=text, lang='en')

            # Save audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                tts.save(temp_audio_file.name)
                audio_file = temp_audio_file.name

            # Read the file and encode it to base64
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()

            # Generate HTML to autoplay the audio
            audio_html = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """
            # Use Streamlit's markdown function to render the HTML
            st.markdown(audio_html, unsafe_allow_html=True)

            # Optionally, delete the temporary file after playback
            # os.remove(audio_file)
        except Exception as e:
            st.error(f"An error occurred while processing text-to-speech: {e}")
    else:
        st.warning("No text provided for speech synthesis.")
