import streamlit as st
import requests
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from flask import Flask, request, render_template, jsonify

# ==========================
# Load trained models
# ==========================
reg_model = joblib.load("reg_pipeline.pkl")   # regression pipeline
clf_model = joblib.load("clf_pipeline.pkl")   # classification pipeline

API_KEY = "d985a85e680ff6ef6df85acd61fe9ab3"

# ==========================
# Helper: Get weather data
# ==========================
def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# ==========================
# Helper: Preprocess for model
# ==========================
def preprocess_weather_for_model(api_data):
    """Preprocess API weather data into a feature set for model prediction."""
    main = api_data["main"]
    wind = api_data["wind"]

    # Temperature calculations
    min_temp = main.get("temp_min", main["temp"])
    max_temp = main.get("temp_max", main["temp"])
    avg_temp = (min_temp + max_temp) / 2

    # Humidity calculations
    humidity = main.get("humidity", 50)
    min_humidity = max(humidity - 5, 0)
    max_humidity = min(humidity + 5, 100)
    avg_humidity = (min_humidity + max_humidity) / 2
    humidity_range = max_humidity - min_humidity

    # Wind and rainfall data
    wind_speed = wind.get("speed", 0)
    wind_range = wind_speed * 0.3
    rainfall = api_data.get("rain", {}).get("1h", 0)

    # Derived features
    temp_range = max_temp - min_temp
    features = pd.DataFrame([{
        "Avg_Humidity": avg_humidity,
        "AvgTemp_AvgHumidity": avg_temp * avg_humidity,
        "precipitation": rainfall,
        "Max Humidity (%)": max_humidity,
        "Month": datetime.now().month,
        "WindInteraction": wind_range * wind_speed,
        "Temp_Range": temp_range,
        "Wind_Range": wind_range,
        "precipitation_flag": int(rainfall > 0),
        "Temp_Humidity_Range": temp_range * humidity_range,
        "temp_rain_interaction": temp_range * rainfall
    }])

    return features

# ==========================
# Helper: Prediction

def predict_rainfall(api_data):
    features = preprocess_weather_for_model(api_data)

    # Regression
    rain_mm_log = float(reg_model.predict(features)[0])
    rain_mm = float(np.expm1(rain_mm_log))  # reverse log1p -> ensure Python float

    # Classification
    rain_class = int(clf_model.predict(features)[0])

    # Determine human-readable message
    if rain_class == 1:
        rain_text = (
            "🌦 Light Rain – carry an umbrella ☂️" if rain_mm < 2 else
            "🌧 Moderate Rain – roads might be wet!" if rain_mm < 10 else
            "⛈ Heavy Rain – stay safe outdoors ⚠️"
        )
    else:
        rain_text = "☀ No Rain – enjoy the clear sky!"

    return {
        "rain_mm": round(rain_mm, 2),
        "rain_text": rain_text,
        "rain_class": rain_class
    }


# ==========================
# Streamlit UI
# ==========================
st.set_page_config(page_title="Weather Guide", page_icon="🌦", layout="centered")

st.markdown("<h1 style='text-align: center; font-size: 45px;'>🌍 Weather Guide</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Get live weather info worldwide & predict rainfall in Telangana</p>", unsafe_allow_html=True)

page = st.sidebar.radio("📌 Navigate", ["🌍 Weather Info", "🌧 Rainfall Prediction"])

# ==========================
# Page 1: Global Weather Info
# ==========================
if page == "🌍 Weather Info":
    st.header("🌍 Global Weather Information")
    city = st.text_input("Enter City Name (e.g., London, New York, Hyderabad):")

    if st.button("Get Weather 🌡️"):
        data = get_weather_data(city)
        if data:
            st.success(f"✅ Weather in {city.title()}")
            st.write("**🌤 Condition:**", data["weather"][0]["description"].title())
            st.write("**🌡 Temperature:**", data["main"]["temp"], "°C")
            st.write("**💧 Humidity:**", data["main"]["humidity"], "%")
            st.write("**🌀 Wind Speed:**", data["wind"]["speed"], "m/s")
        else:
            st.error("⚠️ City not found or API error.")

# ==========================
# Page 2: Telangana Rainfall Prediction
# ==========================
elif page == "🌧 Rainfall Prediction":
    st.header("🌧 Telangana Rainfall Prediction")
    district = st.text_input("Enter Telangana District:")

    if st.button("Predict Rainfall 🌦"):
        city = district + ",IN"   # to query OpenWeather
        data = get_weather_data(city)

        if data:
            st.subheader(f"📍 Live Weather in {district.title()}")
            st.write("**🌡 Temperature:**", data["main"]["temp"], "°C")
            st.write("**💧 Humidity:**", data["main"]["humidity"], "%")
            st.write("**🌀 Wind Speed:**", data["wind"]["speed"], "m/s")

            result = predict_rainfall(data)
            rain_mm, rain_text = result["rain_mm"], result["rain_text"]

            st.subheader("🌦 Prediction Result")
            st.metric("Predicted Rainfall (mm)", f"{rain_mm:.2f}")
            st.markdown(f"<h3 style='color:blue;'>{rain_text}</h3>", unsafe_allow_html=True)
        else:
            st.error("⚠️ District not found or API error.")

# ==========================
# Flask API for Prediction
# ==========================
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint: /predict
    Method: POST
    Description:
        Takes form data (numerical values), converts them to floats,
        passes them to a trained model, and returns a JSON response
        with the prediction result.
    """
    try:
        # Convert form input values to floats
        values = [float(x) for x in request.form.values()]

        # Perform prediction
        pred = model.predict([np.array(values)])

        # Convert NumPy scalar to native Python type for JSON serialization
        prediction_value = float(pred[0])

        # Return the prediction as JSON
        return jsonify(prediction=prediction_value)

    except Exception as e:
        # Handle unexpected errors gracefully
        return jsonify(error=str(e)), 400



if __name__ == "__main__":
    print("The Flask prediction API is running at: http://127.0.0.1:5000/predict")
    app.run(debug=True, host='0.0.0.0', port=5000)
