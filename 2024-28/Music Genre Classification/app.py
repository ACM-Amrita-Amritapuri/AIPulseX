import streamlit as st
import tensorflow as tf
import librosa  # type: ignore
import numpy as np
import os
import matplotlib.pyplot as plt
import tempfile
import pandas as pd

class_names = ['blues', 'classical', 'country', 'disco', 'hiphop','jazz', 'metal', 'pop', 'reggae', 'rock']
# Creating functions to preprocess audio files and load model
def preprocess_file(file_path,n_mfcc=40,max_len=1300):
    try:
        y,sr=librosa.load(file_path,duration=30)
        mfcc=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=n_mfcc)
        if mfcc.shape[1] <max_len:
                        pad_width=max_len-mfcc.shape[1]
                        mfcc=np.pad(mfcc,((0,0),(0,pad_width)),mode='constant')
        else:
            mfcc=mfcc[:, :max_len]
        mfcc=mfcc.reshape(n_mfcc,max_len,1)
        mfcc=np.expand_dims(mfcc,axis=0)
        return mfcc 
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
    st.warning("Please upload a WAV file to begin.")
