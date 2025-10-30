import streamlit as st
import requests
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# ==========================
# Load trained models
# ==========================
reg_model = joblib.load("reg_pipeline.pkl")   # Regression pipeline
clf_model = joblib.load("clf_pipeline.pkl")   # Classification pipeline

API_KEY = "d985a85e680ff6ef6df85acd61fe9ab3"

# ==========================
# Helper: Fetch weather data
# ==========================
def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# ==========================
# Helper: Preprocess for Model
# ==========================
def preprocess_weather_for_model(api_data):
    main = api_data["main"]
    wind = api_data["wind"]

    min_temp = main.get("temp_min", main["temp"])
    max_temp = main.get("temp_max", main["temp"])
    avg_temp = (min_temp + max_temp) / 2

    humidity = main.get("humidity", 50)
    min_humidity = max(humidity - 5, 0)
    max_humidity = min(humidity + 5, 100)
    avg_humidity = (min_humidity + max_humidity) / 2
    humidity_range = max_humidity - min_humidity

    wind_speed = wind.get("speed", 0)
    wind_range = wind_speed * 0.3  # assumption

    temp_range = max_temp - min_temp
    rainfall = api_data.get("rain", {}).get("1h", 0)

    features = pd.DataFrame([{
        "Avg_Humidity": avg_humidity,
        "AvgTemp_AvgHumidity": avg_temp * avg_humidity,
        "precipitation": rainfall,
        "Max Humidity (%)": max_humidity,
        "Month": datetime.now().month,
        "WindInteraction": wind_range * wind_speed,
        "Temp_Range": temp_range,
        "Wind_Range": wind_range,
        "precipitation_flag": 1 if rainfall > 0 else 0,
        "Temp_Humidity_Range": temp_range * humidity_range,
        "temp_rain_interaction": temp_range * rainfall
    }])

    return features

# ==========================
# Prediction Handler
# ==========================
def predict_rainfall(api_data):
    features = preprocess_weather_for_model(api_data)

    # Regression
    rain_mm_log = reg_model.predict(features)[0]
    rain_mm = np.expm1(rain_mm_log)

    # Classification
    rain_class = clf_model.predict(features)[0]
    if rain_class == 1:
        if rain_mm < 2:
            rain_text = "🌦 Light Rain – carry an umbrella ☂️"
        elif 2 <= rain_mm < 10:
            rain_text = "🌧 Moderate Rain – roads might be wet!"
        else:
            rain_text = "⛈ Heavy Rain – stay safe outdoors ⚠️"
    else:
        rain_text = "☀ No Rain – enjoy the clear sky!"

    return rain_mm, rain_text

# ==========================
# Streamlit UI
# ==========================
st.set_page_config(page_title="Weather Guide", page_icon="🌦", layout="centered")

st.markdown("<h1 style='text-align: center; color:#0072B2;'>🌍 Weather Guide</h1>", unsafe_allow_html=True)
st.divider()
page = st.sidebar.radio("📌 Navigate", ["🌍 Weather Info", "🌧 Rainfall Prediction"])

# --------------------------
# Page 1: Weather Info
# --------------------------
if page == "🌍 Weather Info":
    city = st.text_input("🏙️ Enter a City Name:")
    if st.button("Check Weather 🌦️"):
        with st.spinner("Fetching live weather data..."):
            data = get_weather_data(city)
        if data:
            st.success(f"✅ Weather in {city.title()}")
            st.write("**🌤 Condition:**", data["weather"][0]["description"].title())
            st.write("**🌡 Temperature:**", f"{data['main']['temp']} °C")
            st.write("**💧 Humidity:**", f"{data['main']['humidity']} %")
            st.write("**🌀 Wind Speed:**", f"{data['wind']['speed']} m/s")
        else:
            st.error("⚠️ Invalid city name or API limit exceeded.")

# --------------------------
# Page 2: Telangana Rainfall
# --------------------------
elif page == "🌧 Rainfall Prediction":
    district = st.text_input("🏘️ Enter Telangana District:")
    if st.button("Predict Rainfall 🌧"):
        city = district + ",IN"
        with st.spinner("Analyzing weather data..."):
            data = get_weather_data(city)
        if data:
            st.subheader(f"📍 Live Weather in {district.title()}")
            st.write("**🌡 Temperature:**", f"{data['main']['temp']} °C")
            st.write("**💧 Humidity:**", f"{data['main']['humidity']} %")
            st.write("**🌀 Wind Speed:**", f"{data['wind']['speed']} m/s")

            rain_mm, rain_text = predict_rainfall(data)

            st.metric("Predicted Rainfall (mm)", f"{rain_mm:.2f}")

            st.markdown(
                f"""
                <div style='padding:12px; background-color:#E3F2FD; border-radius:10px;'>
                <h3 style='color:#0056b3;'>{rain_text}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error("⚠️ District not found or API error occurred.")

# --------------------------
# Footer
# --------------------------
st.divider()
st.markdown(
    f"<p style='text-align:center; font-size:13px; color:gray;'>⏰ Last updated at {datetime.now().strftime('%I:%M %p, %d %b %Y')}</p>",
    unsafe_allow_html=True
)
