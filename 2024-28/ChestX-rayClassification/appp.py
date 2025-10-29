import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import ImageOps

model = tf.keras.models.load_model("cnn_model.h5")

class_names = ['NORMAL', 'PNEUMONIA']

st.title("🩺 Chest X-Ray Classification (CNN)")
st.write("Upload one or more chest X-ray images, and the model will predict if they are **Normal** or show signs of **Pneumonia**.")

uploaded_files = st.file_uploader(
    "Choose chest X-ray images...",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
        img = image.load_img(uploaded_file, target_size=(150, 150), color_mode="grayscale")
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0) 

        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        confidence = np.max(prediction)*100
        # we multiplied with 100 to convert it into percentage

        if predicted_class == "PNEUMONIA":
            st.error(f"🔴 Prediction: **{predicted_class}** ({confidence:.2f}%)")
        else:
            st.success(f"🟢 Prediction: **{predicted_class}** ({confidence:.2f}%)")

        st.write("---")

def teachable_machine_classification(image, model_path):
    model = tf.keras.models.load_model(model_path)

    image = image.convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    img_array = np.asarray(image, dtype=np.float32) / 255.0

    preds = model.predict(img_array)
    return preds

