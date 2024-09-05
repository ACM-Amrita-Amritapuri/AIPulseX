# Gemini AI Voice Bot

Welcome to the **Gemini AI Voice Bot** project! This project leverages Streamlit, SpeechRecognition, and the Gemini AI model to create an interactive voice-enabled chatbot that can understand user speech, process it, and respond intelligently.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Customization](#customization)
- [Contributing](#contributing)

## Project Overview
The Gemini AI Voice Bot is a web-based chatbot interface that listens to user inputs via voice, transcribes the speech into text, and generates responses using the Gemini AI model. The app is built with Streamlit, providing an intuitive and responsive user interface.

## Features
- **Voice Recognition**: Captures user speech and converts it into text.
- **Text-to-Chat Interface**: Displays the transcribed text and the AI's response in a chat format.
- **Responsive Design**: The "Record Voice" button is always centered at the bottom of the chat interface.
- **Customizable**: Easily modify the chatbot's behavior or integrate it with other AI models.

## Installation

### Prerequisites
- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- [PyAudio](https://pypi.org/project/PyAudio/) (for capturing microphone input)

### Setting Up the Project
```bash
# Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the Dependencies
pip install -r requirements.txt

# Set Up PyAudio

## For Windows:
pip install pipwin
pipwin install pyaudio

## For macOS:
brew install portaudio
pip install pyaudio

## For Linux:
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```
# Usage
```bash
# Run the Streamlit App
streamlit run app.py
```

## Interacting with the Bot:
#### 1.Open your web browser and go to http://localhost:8501.
#### 2.Click the "Record Voice" button to start speaking.
#### 3.The bot will transcribe your speech and respond in the chat interface.

# Customization
- **Changing AI Model**: Replace the load_gemini_pro_model() function in app.py with a function that loads your desired model.
- **UI Tweaks**: Modify the CSS in app.py to customize the look and feel of the chat interface and buttons.

# Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss any changes or improvements.