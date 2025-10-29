import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps

# Load model correctly from .h5
model = load_model("hand_gesture_cnn.h5")

# Model input size used during training
img_size = (64, 64)

# Correct class labels
class_labels = ['fist', 'five', 'none', 'okay', 'peace', 'rad', 'straight', 'thumbs']

st.title("🖐 Hand Gesture Recognition")
st.write("Upload a hand gesture image and let the model predict it!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Preprocess image
    image = Image.open(uploaded_file).convert("RGB")
    image = ImageOps.fit(image, img_size, Image.Resampling.LANCZOS)
    img_array = np.asarray(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Prediction
    preds = model.predict(img_array)[0]
    class_index = np.argmax(preds)
    confidence = preds[class_index] * 100

    threshold = 80  # Confidence threshold

    if confidence < threshold:
        st.subheader("❓ Unknown Gesture")
        st.write(f"Confidence too low ({confidence:.2f}%)")
    else:
        st.subheader(f"✅ Predicted Gesture: {class_labels[class_index]}")
        st.write(f"Confidence: {confidence:.2f}%")