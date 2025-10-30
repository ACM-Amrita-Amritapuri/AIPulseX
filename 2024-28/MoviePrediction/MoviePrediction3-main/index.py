import streamlit as st
import pandas as pd
import pickle
import numpy as np

model = pickle.load(open("movie_success_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

st.markdown(
    """
    <style>
    .stApp {
    background: linear-gradient(135deg, #0a0f1f 0%, #16213e 40%, #1c3879 100%);
    color: #FFD700; /* Gold text */
    font-family: 'Cinzel', serif;
    font-weight: 500;
    letter-spacing: 0.6px;
    text-shadow: 0 0 6px rgba(255, 215, 0, 0.3);
    background-attachment: fixed;
    padding: 10px;
    animation: fadeIn 1.5s ease-in-out;
}

/* ====== BACKGROUND LIGHT EFFECTS ====== */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 25% 20%, rgba(255, 215, 0, 0.08), transparent 60%),
                radial-gradient(circle at 75% 80%, rgba(255, 255, 255, 0.05), transparent 70%);
    z-index: -1;
}

/* ====== BUTTON STYLING ====== */
.stButton>button {
    background: linear-gradient(90deg, #b8860b, #ffd700);
    color: #0f1a2e;
    border: 2px solid #FFD700;
    border-radius: 12px;
    padding: 12px 28px;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 0.5px;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.4);
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #ffd700, #ffcc00);
    transform: scale(1.07);
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
}

/* ====== INPUT FIELDS ====== */
.stTextInput>div>input, .stSelectbox>div>select {
    background-color: rgba(255, 255, 255, 0.95);
    color: #000000;
    border: 2px solid #FFD700;
    border-radius: 8px;
    padding: 8px;
    box-shadow: 0 0 8px rgba(255, 215, 0, 0.2);
    transition: 0.3s ease;
}

.stTextInput>div>input:focus, .stSelectbox>div>select:focus {
    border-color: #ffdf00;
    box-shadow: 0 0 12px rgba(255, 215, 0, 0.5);
}

/* ====== STATUS BOXES ====== */
.stSuccess {
    background: linear-gradient(90deg, #228B22, #32CD32);
    color: white;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(50, 205, 50, 0.4);
}

.stError {
    background: linear-gradient(90deg, #B22222, #DC143C);
    color: white;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(220, 20, 60, 0.4);
}

/* ====== HEADINGS ====== */
.header-icon {
    font-size: 42px;
    margin-top: 15px;
    text-align: center;
    color: #FFD700;
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.6);
    animation: pulse 3s infinite alternate;
}

.sub-header {
    font-size: 26px;
    text-align: center;
    color: #FFE55C;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.4);
    font-family: 'Poppins', sans-serif;
}

/* ====== SCROLLBAR ====== */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #FFD700, #b58b00);
    border-radius: 5px;
}
::-webkit-scrollbar-track {
    background: #0a0f1f;
}

/* ====== ANIMATIONS ====== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    from { text-shadow: 0 0 8px rgba(255, 215, 0, 0.3); }
    to { text-shadow: 0 0 18px rgba(255, 215, 0, 0.8); }
}
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app with a cinematic vibe using static elements
st.markdown('<div class="header-icon">🎥 Hollywood Success Oracle ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">🔮 Predict if your movie will be a blockbuster! 🎞️</div>', unsafe_allow_html=True)

# Static visual element with local image
st.image("popcorn.webp", caption="🍿 Curtains Up! 🎬", use_container_width=True)

# Input fields with a creative twist
# -------------------------------------------------------------
# 🎬 Movie Spell Casting Interface (Streamlit UI)
# -------------------------------------------------------------

# Display a subheader to introduce the interactive section
st.subheader("🎨 Cast Your Spell!")

# -------------------------------------------------------------
# 💰 Budget Input
# -------------------------------------------------------------
# Allow the user to specify the movie's budget in dollars.
# The slider starts from $1,000 up to $400,000,000 with a default of $5,000,000.
# The 'help' text gives a playful tooltip when hovered.
budget = st.number_input(
    "💰 Budget (in $)",
    min_value=1000,
    max_value=400000000,
    value=5000000,
    step=1000,
    help="Unleash your wallet's magic! 💸"
)

# -------------------------------------------------------------
# ⏳ Runtime Input
# -------------------------------------------------------------
# Ask the user for the duration of the movie in minutes.
# Default is 120 minutes, ranging from 30 to 300.
runtime = st.number_input(
    "⏳ Runtime (minutes)",
    min_value=30,
    max_value=300,
    value=120,
    step=1,
    help="Set the stage duration! ⏰"
)

# -------------------------------------------------------------
# 🎭 Genre Selection
# -------------------------------------------------------------
# Provide a dropdown menu for the user to select the main movie genre.
# Includes a wide variety of genres to choose from.
genres = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
    "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance",
    "Science Fiction", "Thriller", "War", "Western", "Other"
]

main_genre = st.selectbox(
    "🎭 Genre Magic",
    genres,
    help="Choose your movie's soul! 🎥"
)

# -------------------------------------------------------------
# 📅 Release Month Selection
# -------------------------------------------------------------
# Allow the user to choose the release month (1–12).
# Each number corresponds to a calendar month.
release_month = st.selectbox(
    "📅 Release Month",
    list(range(1, 13)),
    help="Pick the perfect premiere date! 🌟"
)


# Process inputs
def get_season(month):
    if month in [5, 6, 7, 8]:
        return "Summer"
    elif month in [11, 12]:
        return "Holiday"
    else:
        return "Other"

release_season = get_season(release_month)

# Create feature vector
features = pd.DataFrame({
    "budget": [budget],
    "runtime": [runtime]
})

# Scale numeric inputs
features[["budget", "runtime"]] = scaler.transform(features[["budget", "runtime"]])

# One-hot encode main_genre (match training columns, drop_first=True)
genre_columns = [f"main_genre_{g}" for g in genres[1:]]  # Drop first genre (Action)
for col in genre_columns:
    features[col] = 0
if main_genre != "Action":  # Adjust if first genre differs
    features[f"main_genre_{main_genre}"] = 1

# One-hot encode release_season (match training columns, drop_first=True)
season_columns = ["release_season_Holiday", "release_season_Other"]  # Summer dropped
for col in season_columns:
    features[col] = 0
if release_season != "Summer":  # Adjust if Summer is expected
    features[f"release_season_{release_season}"] = 1

# Ensure correct feature order and alignment
training_columns = ["budget", "runtime"] + genre_columns + season_columns
features = features.reindex(columns=training_columns, fill_value=0)

# Get model’s expected feature names if available

if hasattr(model, "feature_names_in_"):
    expected_features = model.feature_names_in_.tolist()
    missing = [f for f in expected_features if f not in features.columns]
    extra = [f for f in features.columns if f not in expected_features]

    for col in missing:
        features[col] = 0
    features = features.reindex(columns=expected_features, fill_value=0)

    if missing or extra:
        st.info(f"Auto-aligned features — {len(missing)} added, {len(extra)} ignored.")
else:
    # Improved feature mismatch handling
    expected_features = 23
    actual_features = len(features.columns)

    if actual_features != expected_features:
        st.warning(f"⚠️ Feature mismatch detected: Expected {expected_features} features, but received {actual_features}.")
        st.info("🧩 Tip: This may happen if new genres or input fields were added/removed. Please ensure your dataset matches the model training schema.")
        st.write("🔍 Current input features:", ", ".join(features.columns))

        # Auto-adjust columns if fewer/more features are present
        try:
            missing_cols = [f"feature_{i}" for i in range(expected_features - actual_features)] if actual_features < expected_features else []
            for col in missing_cols:
                features[col] = 0  # Default fill for missing features

            if len(features.columns) > expected_features:
                features = features.iloc[:, :expected_features]  # Trim extra features

            st.success("✨ Automatically aligned feature dimensions to match model expectations.")
        except Exception as e:
            st.error(f"🚨 Unable to adjust features automatically: {e}")
            st.stop()

# Prediction
if st.button("🎇 Unveil the Destiny!"):
    try:
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]
        result = "HIT" if prediction == 1 else "FLOP"
        st.success(f"🏆 Prediction: {result} 🏆\nLights, camera, action! Your movie's fate is sealed! 🎥")
        st.write(f"🌟 Probability of Success: {probability:.2%} 🌟 - The box office whispers its verdict!")
    except ValueError as ve:
        if "feature" in str(ve).lower() or "shape" in str(ve).lower():
            st.error("Feature mismatch! Please check your input values and ensure all required features are present.")
            st.write("Input features shape:", features.shape)
            st.write("Feature names:", ", ".join(features.columns))
        else:
            st.error(f"⚠️ Oops! Magic failed: {str(ve)} ⚠️")
    except Exception as e:
        st.error("An unexpected error occurred. Please try again or check your input.")
        st.write("Technical details:", str(e))

@app.route("/predict", methods=["GET"])
def predict():
    values = [float(x) for x in request.form.values()]
    pred = model.predict(np.array(values))
    return pred