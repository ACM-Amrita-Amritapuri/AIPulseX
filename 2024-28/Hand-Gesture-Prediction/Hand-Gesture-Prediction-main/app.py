import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf
from PIL import Image, ImageOps

# Load trained model
model = tf.saved_model.load("hand_gesture_cnn.h5")

# Define image size (same as training)
img_size = (64, 64)

# Correct class labels (from train_generator.class_indices)
class_labels = ['fist', 'five', 'none', 'okay', 'peace', 'rad', 'straight', 'thumbs']

st.title("🖐 Hand Gesture Recognition")
st.write("Upload a hand gesture image and let the model predict it!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Preprocess image (must match training preprocessing)
    image = Image.open(uploaded_file)
    image = image.convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    img_array = np.asarray(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Prediction
    preds = model.predict(img_array)
    class_index = np.argmax(preds)
    confidence = np.max(preds) * 100

    # Get the predicted class label
    label_idx = model.predict_classes(img_array)[0]

    threshold = 80

    if confidence < threshold:
        st.subheader("❓ Unknown Gesture")
        st.write(f"Confidence too low ({confidence:.2f}%)")
    else:
        st.subheader(f"✅ Predicted Gesture: {class_labels[class_index]}")
        st.write(f"Confidence: {confidence:.2f}%")
