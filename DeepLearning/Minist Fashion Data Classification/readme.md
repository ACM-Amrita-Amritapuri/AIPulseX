# Fashion MNIST Neural Network Model

This project demonstrates how to use the Fashion MNIST dataset to build and train a neural network model for image classification. The dataset consists of images of 10 different categories of fashion items. The project uses Python, TensorFlow, and scikit-learn libraries to preprocess the data, train the model, and evaluate its performance.


## Dataset
The Fashion MNIST dataset is composed of 70,000 grayscale images, each 28x28 pixels, representing 10 different categories of fashion items. The dataset is divided into:

Training set: 60,000 images
Test set: 10,000 images


#### Classes

The dataset includes the following classes:

- T-shirt/top
- Trouser
- Pullover
- Dress
- Coat
- Sandal
- Shirt
- Sneaker
- Bag
- Ankle boot


## Requirements

- Python 3.x
- TensorFlow
- scikit-learn
- Matplotlib
- NumPy
- Pandas

## Steps Followed

1. **Data Loading**
   - Fetch the Fashion MNIST dataset using `fetch_openml` from scikit-learn.
   - Load the dataset into variables `X` (features) and `y` (labels).

2. **Data Visualization**
   - Display sample images for each class to understand the dataset.
   - Use Matplotlib to create visualizations of images.

3. **Data Preprocessing**
   - Convert labels to integer format.
   - Normalize pixel values by dividing by 255.
   - Split the dataset into training and testing sets using `train_test_split`.

4. **Model Building**
   - Define a neural network architecture using TensorFlow's Keras API.
   - Create a model with input, hidden, and output layers.
   - Compile the model with an optimizer and loss function.

5. **Model Training**
   - Train the neural network model on the training dataset.
   - Monitor training progress and adjust parameters as needed.

6. **Model Evaluation**
   - Evaluate the model's performance on the test dataset.
   - Analyze accuracy and loss metrics.

7. **Prediction Visualization**
   - Display sample predictions alongside the original images.
   - Compare model predictions with actual labels.
