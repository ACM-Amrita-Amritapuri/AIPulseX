import os

import streamlit as st
import speech_recognition as sr
from streamlit_option_menu import option_menu
from audio_recorder_streamlit import audio_recorder

from gemini_utility import load_gemini_pro_model
from Audio_to_text import recognize_speech
from text_to_speech import Output_Speech
working_directory = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Gemini API Voice BOT",
    layout="centered"
)
with st.sidebar:

    selected = option_menu("Gemini AI",["Voice Bot",
                           # "Image Captioning",
                           # "Embed Text"
                                        ],
                           menu_icon= 'robot',
                           default_index=0)

def translate_role_for_streamlit(user_role):
    if user_role == 'model':
        return "assistant"
    else:
        return user_role



if selected == "Voice Bot":

    model = load_gemini_pro_model()  # Ensure this function is correctly defined

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.title("Voice Bot")

    # Chat History
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    text = recognize_speech()

    user_prompt = text

    if user_prompt:
        if user_prompt == "Audio should be given qwertyu":
            with st.chat_message("assistant"):
                st.markdown("I was not able to understand what you said (or) there was no audio command")
        else:
            st.chat_message('user').markdown(user_prompt)

            gemini_response = st.session_state.chat_session.send_message(user_prompt)
            Output_Speech(gemini_response.text)  # Call the Output_Speech function

            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)