Here's the README file for your "Sound Emotion Recognition" project:

# Sound Emotion Recognition 🎧

## Introduction 🎙️

The Sound Emotion Recognition project aims to classify human emotions from speech in audio files. This model leverages the natural variations in voice, such as tone and pitch, which often reflect underlying emotions.

## Project Details 📊

- **Goal**:

  - To develop a classifier model that recognizes human emotions from speech audio files.

- **Workflow**:
  - **Audio Preprocessing**:
    - The audio files undergo several preprocessing steps, including noise reduction and time stretching.
    - Standard feature extraction techniques like Root Mean Square (RMS), Zero-Crossing Rate (ZCR), and Mel-Frequency Cepstral Coefficients (MFCC) are applied to extract relevant features from the audio data.
  - **Model**:
    - The **RandomForestClassifier** is used as the model, achieving an accuracy of approximately 80%.
  - **Implementation**:
    - The project is implemented using the Python library **Streamlit**, which provides a user-friendly web interface for interaction.
  - **Datasets**:
    - The **Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS)** dataset is used in this project to train and evaluate the model.

## Challenges & Solutions 🚧

- **Audio Preprocessing**:

  - **Challenge**: Finding the right library and understanding its functionality for audio preprocessing.
  - **Solution**: After exploring available libraries and understanding their operations, the appropriate preprocessing steps were implemented successfully.

- **Model Accuracy**:
  - **Challenge**: Initially, the model showed low accuracy due to insufficient data extraction methods and preprocessing techniques.
  - **Solution**: By increasing the number of feature extraction methods and enhancing preprocessing techniques, the model's accuracy improved significantly to approximately 80%.

## Conclusion 📝

The project demonstrates the effective use of machine learning in recognizing emotions from speech audio. The integration of advanced preprocessing and feature extraction techniques with a RandomForestClassifier shows promising results, achieving a solid accuracy with a user-friendly web interface.

## Team 👥

- **Abhinav M Nair**
