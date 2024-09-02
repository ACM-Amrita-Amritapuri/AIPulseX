# Image Classification using VGG16

This project demonstrates an image classification model built using the VGG16 architecture pre-trained on the ImageNet dataset. The model is fine-tuned on a custom dataset for binary classification.

## Project Structure

*   `train/`: Directory containing the training images, organized into subdirectories for each class.
*   `test/`: Directory containing the test images, organized into subdirectories for each class.
*   `model.py`: Script containing the model definition, data preprocessing, training, and evaluation.
*   `README.md`: Documentation for the project.

## Requirements

*   Python 3.x
*   TensorFlow
*   Keras
*   NumPy
*   Matplotlib

Install the necessary packages using `pip`:

```
pip install tensorflow keras numpy matplotlib
```

## Model Architecture

The model architecture is based on the VGG16 network, with the following components:

1.  **VGG16 Base**: The VGG16 model pre-trained on ImageNet is used as the base model, excluding the top layers.
2.  **Flatten Layer**: The output from the VGG16 model is flattened into a 1D feature vector.
3.  **Dense Layer**: A fully connected layer with 2 output neurons (for binary classification) and a softmax activation function.

## Data Augmentation

Data augmentation is performed on the training and testing datasets to improve model generalization. The following augmentations are applied:

*   Rotation (up to 40 degrees)
*   Width and Height Shifts
*   Shear
*   Zoom
*   Horizontal Flip

## Training

The model is compiled with the Adam optimizer, binary cross-entropy loss function, and accuracy as the evaluation metric. The model is trained for 2 epochs.

## Evaluation

After training, the model's performance is evaluated on the test dataset, and the validation loss and accuracy are printed.

## How to Run

1.  Prepare your dataset:
    *   Place your training images in the `train/` directory, organized into subdirectories for each class.
    *   Place your test images in the `test/` directory, organized similarly.
2.  Run the script:
    
    ```
    python model.py
    ```
    
3.  The script will output the validation loss and accuracy after training.

## Results

After running the model, you will see the validation loss and accuracy printed in the console.
