import streamlit as st
import tensorflow as tf
import librosa  # type: ignore
import numpy as np
import os
import matplotlib.pyplot as plt
import tempfile
import pandas as pd

# Define class names
class_names = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']

# --- Preprocessing and Model Loading ---

def preprocess_file(file_path, n_mfcc=40, max_len=1300):
    """
    Loads an audio file, computes its MFCC, and formats it
    for the model. Also returns the raw MFCC for plotting.
    """
    try:
        y, sr = librosa.load(file_path, duration=30)
        # Compute MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        
        # Pad or truncate the MFCC
        if mfcc.shape[1] < max_len:
            pad_width = max_len - mfcc.shape[1]
            mfcc_padded = np.pad(mfcc, ((0, 0), (0, pad_width)), mode='constant')
        else:
            mfcc_padded = mfcc[:, :max_len]
        
        # Reshape for the model (add batch and channel dimensions)
        mfcc_processed = mfcc_padded.reshape(n_mfcc, max_len, 1)
        mfcc_processed = np.expand_dims(mfcc_processed, axis=0)
        
        # Return both the processed tensor and the plottable MFCC
        return mfcc_processed, mfcc_padded
        
    except Exception as e:
        st.error(f"Error processing audio file: {e}")
        return None, None

@st.cache_resource
def load_trained_model():
    """Loads the pre-trained Keras model."""
    try:
        model = tf.keras.models.load_model("Model.keras")
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Load the model
model = load_trained_model()

# --- Streamlit App UI ---

st.set_page_config(page_title="Music Genre Classifier", layout="centered", page_icon="🎸")
st.title("Music Genre Classification App 🎶")
st.markdown("Upload a `.wav` audio file and the model will predict its genre.")

# File uploader
file = st.file_uploader("Upload your .wav file", type=["wav"])

if file is not None and model is not None:
    # Display the audio player
    st.audio(file, format="audio/wav")
    
    with st.spinner("Analyzing your music... 🎶"):
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # Process the file
        features, mfcc_plot_data = preprocess_file(tmp_path)
        
        # Remove the temporary file
        os.remove(tmp_path)
        if features is not None:
            preds=model.predict(features)[0]
            predicted_genre=class_names[np.argmax(preds)]
            confidence=preds[np.argmax(preds)]*100
            st.success(f"**Predicted Genre:** {predicted_genre}")
            st.info(f"CONFIDENCE: 'x`{confidence:.2f}%'")
            # Displaying the full prediction distribution
            fig, ax = plt.subplots()
            ax.pie(preds, labels=class_names, autopct='%1.1f%%',
                   startangle=140, textprops={'fontsize': 8})
            ax.axis('equal')
            st.pyplot(fig)

else:
    # Landing page info
    st.info("Please upload a WAV file to begin analysis.")
    
    with st.expander("How does this work?"):
        st.markdown("""
            <p>
            This app uses a Deep Learning model (a Convolutional Neural Network) trained 
            on the <b>GTZAN Dataset</b>, a standard benchmark for music genre classification.
            </p>
            <p>
            When you upload a file, the app does the following:
            <ol>
                <li><b>Load Audio:</b> Reads the first 30 seconds of the `.wav` file.</li>
                <li><b>Extract Features:</b> Calculates the Mel-Frequency Cepstrum (MFCC), 
                    which represents the sound's unique timbre and texture.</li>
                
                <li><b>Pad/Truncate:</b> Resizes the MFCC to a fixed length (1300 frames) 
                    so all inputs are the same size.</li>
                <li><b>Predict:</b> Feeds this data into the trained model to get a 
                    probability score for each of the 10 genres.</li>
            </ol>
            </p>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("Created with Streamlit and TensorFlow.")
