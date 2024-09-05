import streamlit as st
import speech_recognition as sr

# Streamlit app title
# st.title("Speech-to-Text Converter")

# Initialize recognizer


# Function to recognize speech
def recognize_speech():
    if st.button("INPUT COMMAND 🎙️"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Please speak into the microphone...")
            audio = recognizer.listen(source)
            try:
                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Audio should be given qwertyu"
            except sr.RequestError :
                return "Audio should be given qwertyu"

# Streamlit button to start recording
# if st.button("Start Recording"):
#     st.write("Recording...")
#     text = recognize_speech()
#     st.write("You said:", text)
