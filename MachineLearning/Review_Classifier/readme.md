# Movie Review Classifier 🎬

## Introduction 📘

The Movie Review Classifier project is designed to automatically analyze and classify the sentiment expressed in movie reviews as either positive or negative. This system leverages machine learning techniques to accurately predict sentiment, providing valuable insights into audience reactions.

## Project Details 📊

- **Goal**:

  - The primary objective is to develop a classifier that can effectively distinguish between positive and negative sentiments in movie reviews using the IMDB dataset.

- **Workflow**:
  - **Importing Libraries**:
    - Essential libraries for data manipulation, machine learning, and evaluation are imported.
  - **Loading Dataset**:
    - The IMDB dataset is loaded into a Pandas DataFrame for analysis.
  - **Encoding Sentiment Labels**:
    - Sentiment labels (positive/negative) are converted into numerical form (1/0) using Label Encoder.
  - **Checking Distribution**:
    - The distribution of encoded sentiment labels is checked to ensure class balance.
  - **Creating a Pipeline**:
    - A pipeline is set up to streamline text vectorization and classifier training:
      - **CountVectorizer**: Converts text data into a matrix of token counts.
      - **RandomForestClassifier**: A random forest classifier is used with 5 trees and entropy criterion.
  - **Splitting the Data**:
    - The dataset is split into 80% training and 20% testing sets.
  - **Training the Model**:
    - The pipeline is trained using the training data, converting text to numerical data and training the RandomForestClassifier.
  - **Making Predictions**:
    - The trained model predicts sentiment labels for the test data.
  - **Evaluating the Model**:
    - Model accuracy is assessed by comparing predictions with true labels.
  - **GUI Implementation**:
    - **Tkinter** is used to create a user-friendly interface for sentiment prediction.
    - Widgets are created for user input and displaying predictions.
    - The `process_input()` function handles user input, predicts sentiment, and updates the GUI with results.

## Challenges & Solutions 🚧

- **Feature Extraction**:
  - **Challenge**: Converting text data into a numerical format while retaining context.
  - **Solution**: Utilized CountVectorizer to implement a Bag of Words model.
- **Model Overfitting**:
  - **Challenge**: The model may perform well on training data but poorly on unseen data.
  - **Solution**: Applied cross-validation, pruning, and regularization techniques to improve model generalization.

## Conclusion 📝

This project successfully demonstrates the use of machine learning to classify movie review sentiments. The integration of a RandomForestClassifier within a streamlined pipeline, along with a GUI for easy interaction, highlights the practical application of sentiment analysis in the movie industry.

## Team 👥

- **Vani Sugovind S.R**
- **Siddharth**
