import streamlit as st
import pandas as pd
import pickle
import numpy as np

# ==========================
# Load Model and Scaler
# ==========================
model = pickle.load(open("movie_success_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# ==========================
# Custom Styling (Cinematic Theme)
# ==========================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #080d1f 0%, #15213c 40%, #243b6b 100%);
        color: #FFD700;
        font-family: 'Cinzel', serif;
        letter-spacing: 0.7px;
        background-attachment: fixed;
        animation: fadeIn 1.5s ease-in-out;
    }

    /* Subtle Glow Around App */
    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        background: radial-gradient(circle at 50% 20%, rgba(255, 215, 0, 0.1), transparent 70%);
        z-index: -1;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #cfa707, #ffd700);
        color: #0b132b;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 700;
        border: none;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.08);
        background: linear-gradient(90deg, #ffd700, #ffcc33);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
    }

    /* Success / Error boxes */
    .stSuccess {
        background: linear-gradient(90deg, #2e8b57, #32cd32);
        border-left: 5px solid #00ff88;
        padding: 10px;
        border-radius: 6px;
    }
    .stWarning {
        background: linear-gradient(90deg, #ffcc00, #ffdd55);
        border-left: 5px solid #ffee88;
        padding: 10px;
        border-radius: 6px;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================
# Header Section
# ==========================
st.markdown("<h1 style='text-align:center;'>🎬 Hollywood Fortune Teller 🔮</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:#FFE55C;'>✨ Will your movie shine or flop? Let’s find out! 🍿</h4>", unsafe_allow_html=True)
st.image("popcorn.webp", caption="🍿 Curtain’s Up!", use_container_width=True)

# ==========================
# Input Section
# ==========================
st.subheader("🎭 Cast Your Spell — Enter Movie Details")

budget = st.number_input(
    "💰 Budget (in $)", min_value=1000, max_value=400000000, value=5000000, step=1000,
    help="Enter the production budget. Big dreams need big pockets!"
)

runtime = st.number_input(
    "⏳ Runtime (minutes)", min_value=30, max_value=300, value=120, step=1,
    help="Set the length of your cinematic masterpiece 🎞"
)

genres = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
    "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance",
    "Science Fiction", "Thriller", "War", "Western", "Other"
]
main_genre = st.selectbox("🎨 Main Genre", genres, help="Pick the core theme of your film!")

release_month = st.selectbox("📅 Release Month", list(range(1, 13)), help="Choose the month of release.")

# ==========================
# Feature Engineering
# ==========================
def get_season(month):
    if month in [5, 6, 7, 8]:
        return "Summer"
    elif month in [11, 12]:
        return "Holiday"
    else:
        return "Other"

release_season = get_season(release_month)

features = pd.DataFrame({
    "budget": [budget],
    "runtime": [runtime]
})

features[["budget", "runtime"]] = scaler.transform(features[["budget", "runtime"]])

# Genre encoding
genre_columns = [f"main_genre_{g}" for g in genres[1:]]
for col in genre_columns:
    features[col] = 0
if main_genre != "Action":
    features[f"main_genre_{main_genre}"] = 1

# Season encoding
season_columns = ["release_season_Holiday", "release_season_Other"]
for col in season_columns:
    features[col] = 0
if release_season != "Summer":
    features[f"release_season_{release_season}"] = 1

training_columns = ["budget", "runtime"] + genre_columns + season_columns
features = features.reindex(columns=training_columns, fill_value=0)

# ==========================
# Handle Feature Mismatch
# ==========================
if hasattr(model, "feature_names_in_"):
    expected = model.feature_names_in_.tolist()
    for col in expected:
        if col not in features.columns:
            features[col] = 0
    features = features.reindex(columns=expected, fill_value=0)
else:
    st.warning("Model feature names unavailable — proceeding with default structure.")

# ==========================
# Prediction Button
# ==========================
if st.button("🎇 Reveal the Box Office Fate!"):
    try:
        prediction = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]
        result = "🌟 BLOCKBUSTER HIT!" if prediction == 1 else "💔 FLOP ALERT!"
        st.success(f"🎬 Prediction: {result}")
        st.write(f"✨ Success Probability: **{prob:.2%}**")
    except Exception as e:
        st.error(f"🚨 Something went wrong: {e}")

# ==========================
# API Simulation Section (Instead of Flask)
# ==========================
st.divider()
st.markdown("### 🧩 Simulate API Prediction Call")
st.info("This section mimics an API `/predict` request for local testing.")

if st.button("📡 Test API Prediction"):
    mock_input = [budget, runtime]
    st.write("📤 Sending mock data:", mock_input)
    mock_pred = model.predict(np.array([mock_input]))[0]
    st.write("📥 API Response:", "✅ HIT" if mock_pred == 1 else "❌ FLOP")
