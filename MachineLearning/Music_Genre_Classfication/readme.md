# Music Genre Classification

## Introduction 📘

This project aims to classify music genres using machine learning techniques. The GTZAN dataset, consisting of audio files across 10 genres, is used to train and evaluate the model. The project also includes a GUI implementation for easy genre prediction from audio files.

## Project Details 📊

- **Dataset**:

  - **Source**: The GTZAN dataset was sourced from Kaggle.
  - **Link**: [GTZAN Music Genre Classification Dataset](https://www.kaggle.com/datasets/andradaolteanu/gtzan-dataset-music-genre-classification?resource=download)
  - **Contents**:
    - 10 genres with 100 audio files each, all 30 seconds long.
    - CSV files containing extracted features from the audio files.

- **Data Loading**:

  - Loaded data from two CSV files into Pandas DataFrames and concatenated them into a single dataframe for further processing.

- **Preprocessing**:

  - Dropped unnecessary columns from the dataframe.
  - Transformed categorical data into a numeric format.
  - Created a lookup dictionary for mapping numerical codes to genre labels.
  - Split the data into 75% training and 25% testing sets.
  - Standardized features using StandardScaler for better performance of the KNN model.

- **Model Training**:

  - Used Random Forests to evaluate feature importance.
  - Developed a K-Nearest Neighbors (KNN) model, optimized through GridSearchCV for the best hyperparameters.

- **Model Evaluation**:

  - Evaluated the model's effectiveness by analyzing accuracy and generating a classification report.

- **GUI Implementation**:
  - Designed a user interface using the Tkinter library.
  - Implemented a `predict_genre_by_filename` function to predict genres from selected audio files.

## Challenges & Solutions 🚧

- **Feature Scaling**:

  - **Challenge**: The performance of the KNN model was affected by inconsistent scaling of training and testing features.
  - **Solution**: Applied StandardScaler to both training and testing data, which improved the model’s performance by ensuring consistent scaling across datasets.

- **Optimizing Model Performance**:
  - **Challenge**: The initial KNN model had low accuracy in classifying music genres.
  - **Solution**: Used GridSearchCV to find the best hyperparameters, significantly improving the model's accuracy based on cross-validation results.

## Conclusion 📝

The project successfully implemented a KNN model for music genre classification, enhanced through feature scaling and hyperparameter optimization. The inclusion of a user-friendly GUI further extends the practical application of the model, allowing users to easily predict music genres.

## Team 👥

- **Meghana**
- **Snigdha**
