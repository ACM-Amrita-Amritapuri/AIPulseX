# Movie Recommendation System

## Introduction 📘

The goal of this project is to build a machine learning model that can recommend movies to users based on either genre or movie title. The system is designed to enhance user experience by offering personalized movie recommendations using advanced clustering techniques.

## Project Details 📊

- **Dataset**: The dataset consists of 5,000 movies, including various features such as title, genre, and other metadata.
- **Preprocessing**: Unnecessary features were dropped, and the dataset was restructured to focus on relevant information. Genres were transformed into features to facilitate model training.
- **Recommendation Methods**:
  - **By Genre**: Provides recommendations based on the selected genre.
  - **By Movie Title**: Suggests movies similar to a given movie title.
- **Model Used**: K-Means Clustering, an unsupervised learning technique, was used to group movies with similar genres into clusters.
- **User-Friendly Feature**: The system is designed to be case-sensitive, making it more intuitive for users when entering movie titles.

## Challenges & Solutions 🚧

- **Preprocessing and Feature Extraction**:

  - **Challenge**: Deciding which features to keep and how to preprocess the data for effective model training.
  - **Solution**: Dropped unnecessary features and used genres as the primary features for clustering.

- **Classifier Selection**:
  - **Challenge**: Selecting an appropriate classifier that could efficiently handle the large and diverse dataset while maintaining high accuracy.
  - **Solution**: After experimenting with several classifiers, such as K-Nearest Neighbors and Decision Trees, we chose K-Means Clustering for its ability to group similar movies based on genre effectively.

## Results 📈

The system successfully recommends movies either by genre or by similar titles. The use of K-Means Clustering ensures that movies with similar characteristics are grouped together, providing accurate and relevant recommendations to users.

## Conclusion 📝

This project effectively demonstrates the application of unsupervised learning techniques, particularly K-Means Clustering, to build a robust movie recommendation system. The system's user-friendly interface and accurate recommendations make it a valuable tool for users seeking personalized movie suggestions.

## Team 👥

- **K. Madhuri**
- **Y. Madhav**
