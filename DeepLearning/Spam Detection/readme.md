# Spam Email Detection

This project implements a spam email detection system using deep learning. The model is trained on a dataset of email texts labeled as "Spam" or "Ham" (Not Spam) and uses a neural network to classify new emails based on their content.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Dataset](#dataset)
- [Model Architecture](#model-architecture)
- [Setup](#setup)
- [Usage](#usage)
- [Results](#results)
- [Future Work](#future-work)
- [Acknowledgments](#acknowledgments)

## Introduction
Spam emails are a prevalent issue in the digital world, and identifying them is crucial to prevent fraud and protect sensitive information. This project aims to classify emails into:
- **Spam**: Unwanted or fraudulent emails.
- **Ham**: Legitimate or useful emails.

## Features
- Preprocessing of email data to clean and tokenize text.
- Neural network trained with embeddings for text representation.
- Binary classification using TensorFlow/Keras.

## Dataset
The dataset is provided as a CSV file with two fields:
- **`label`**: Specifies whether the email is "Spam" or "Ham."
- **`text`**: Contains the email content.

### Preprocessing Steps
- Extract labels (`Spam` or `Ham`) and clean email text.
- Tokenize the email content and pad sequences for uniformity.

### Dataset Summary
- Total Samples: 147,719
- Class Distribution:
  - Ham: 74,537
  - Spam: 73,182

## Model Architecture
The neural network is built using TensorFlow/Keras:
1. **Embedding Layer**: Converts tokens to dense vectors.
2. **Global Average Pooling Layer**: Reduces dimensionality of embeddings.
3. **Dense Layer**: Fully connected layer with ReLU activation.
4. **Output Layer**: Fully connected layer with sigmoid activation for binary classification.

### Hyperparameters
- Vocabulary Size: `500`
- Sequence Length: `50`
- Embedding Dimension: `16`
- Loss Function: `Binary Crossentropy`
- Optimizer: `Adam`
- Metrics: `Accuracy`

## Usage

### Steps to Run the Model
1. **Upload the Dataset**: Upload the dataset file `spam_Emails_data.csv` to your Google Drive.
2. **Run the Script**: Open the provided script in a Jupyter Notebook or Google Colab and execute the cells sequentially.
3. **Train the Model**: The script automatically trains the model using the dataset.
4. **Test the Model**: Use the following function to test the model with custom email messages:

   ```python
   predict_spam("Your custom email message here")
## Results

The spam email detection model was evaluated on the dataset and achieved the following performance metrics:

- **Validation Accuracy**: **86.67%**
- **Validation Loss**: **0.3178**
