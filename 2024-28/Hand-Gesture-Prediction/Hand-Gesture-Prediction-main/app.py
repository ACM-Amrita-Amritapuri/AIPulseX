import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image, ImageOps
import tensorflow as tf

# Load the trained CNN model
model = load_model("hand_gesture_cnn.h5")

# Define the expected image size
IMG_SIZE = (64, 64)

# Gesture class labels
CLASS_LABELS = ['fist', 'five', 'none', 'okay', 'peace', 'rad', 'straight', 'thumbs']

# Page title and description
st.title("✋ Hand Gesture Recognition App")
st.markdown("### Upload an image of your hand gesture and let the AI model predict it!")

# File uploader widget
uploaded_file = st.file_uploader("📤 Upload your gesture image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="🖼️ Uploaded Image", use_container_width=True)
    st.write("Processing... 🔍")

    # Preprocess the uploaded image
    image = Image.open(uploaded_file).convert("RGB")
    image = ImageOps.fit(image, IMG_SIZE, Image.Resampling.LANCZOS)
    img_array = img_to_array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Make prediction
    preds = model.predict(img_array)
    class_index = np.argmax(preds)
    confidence = np.max(preds) * 100

    # Confidence threshold
    CONF_THRESHOLD = 80

    st.divider()  # 👈 adds a nice horizontal line for visual separation

    if confidence < CONF_THRESHOLD:
        st.warning(f"❓ Unknown Gesture — Confidence too low ({confidence:.2f}%)")
    else:
        st.success(f"✅ Predicted Gesture: **{CLASS_LABELS[class_index].capitalize()}**")
        st.info(f"Model Confidence: {confidence:.2f}%")

st.caption("Built with ❤️ using Streamlit & TensorFlow")

