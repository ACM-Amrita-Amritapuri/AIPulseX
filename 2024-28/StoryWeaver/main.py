import os
import warnings
import asyncio
import time
import string
import traceback
import numpy as np
import pickle
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from colorama import Fore, Style

# -------------------------------------------------------------
# 🧠 Environment & Warnings Setup
# -------------------------------------------------------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   # Suppress INFO/WARN logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimization
warnings.filterwarnings('ignore')

# -------------------------------------------------------------
# ⚙️ Constants
# -------------------------------------------------------------
MODEL_PATH = r'Models\best_story_model.keras'
TOKENIZER_NAME = r'Models\tokenizer.pickle'
MAX_SEQUENCE_LENGTH = 60

# -------------------------------------------------------------
# 🚀 Model & Tokenizer Loading
# -------------------------------------------------------------
print(Fore.CYAN + "\n[INFO] Loading model and tokenizer..." + Style.RESET_ALL)
model = load_model(MODEL_PATH)

with open(TOKENIZER_NAME, 'rb') as f:
    tokenizer = pickle.load(f)

print(Fore.GREEN + f"✅ Model loaded successfully (Max Seq Length: {MAX_SEQUENCE_LENGTH})\n" + Style.RESET_ALL)

# Store app start time for uptime tracking
START_TIME = time.time()


# -------------------------------------------------------------
# 🧩 Story Generation Logic
# -------------------------------------------------------------
async def generate_story(prompt):
    def clean_data(text):
        text = str(text).lower()
        text = ''.join([i for i in text if i not in string.punctuation])
        text = text.encode('utf8').decode('ascii', 'ignore')
        return text

    if not prompt or not prompt.strip():
        return "Error: Empty prompt provided."
    text = prompt
    next_words = 60
    for _ in range(next_words):
        cleaned_prompt = clean_data(prompt)
        tokens = tokenizer.texts_to_sequences([cleaned_prompt])[0]

        if not tokens:
            return prompt.title()

        tokens = tokens[-(MAX_SEQUENCE_LENGTH - 1):]
        tokens = pad_sequences([tokens], maxlen=MAX_SEQUENCE_LENGTH, padding='pre')

        prediction = model.predict(tokens, verbose=0)
        prediction = prediction[0] / 0.7  # temperature
        prediction = np.exp(prediction) / np.sum(np.exp(prediction))

        predicted_index = np.random.choice(len(prediction), p=prediction)
        output = ""

        for word, index in tokenizer.word_index.items():
            if index == predicted_index:
                output = word
                break
        if output:
            prompt += ' ' + output
            if output in ['.', '!', '?'] or len(prompt.split()) > 100:
                break
        else:
            break

    return prompt.strip().capitalize()


def handler(prompt):
    return asyncio.run(generate_story(prompt))


# -------------------------------------------------------------
# 🌐 Flask App Setup
# -------------------------------------------------------------
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)


@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')


@app.route('/style.css')
def serve_css():
    return send_from_directory('frontend', 'style.css')


@app.route('/script.js')
def serve_js():
    return send_from_directory('frontend', 'script.js')


# -------------------------------------------------------------
# ✨ Generate Story Endpoint
# -------------------------------------------------------------
@app.route('/generate', methods=['POST'])
def give_response():
    try:
        data = request.get_json()
        seed = data.get("seed_text", "").strip().lower()
        next_words = data.get('next_words', 50)

        if not seed:
            return jsonify({"error": "Please provide a valid seed text."}), 400
        if len(seed.split()) < 2:
            return jsonify({"error": "Prompt too short. Try adding more context."}), 400

        story = handler(seed)
        print(Fore.YELLOW + f"[STORY GENERATED] Prompt: '{seed}' → Result Length: {len(story.split())} words" + Style.RESET_ALL)

        return jsonify({"story": story}), 200

    except Exception as e:
        print(Fore.RED + f"❌ Error during story generation: {e}" + Style.RESET_ALL)
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred during story generation."}), 500


# -------------------------------------------------------------
# 🩺 Health Check Endpoint
# -------------------------------------------------------------
@app.route('/health', methods=['GET'])
def check_health():
    uptime = round(time.time() - START_TIME, 2)
    return jsonify({
        "status": "ok",
        "message": "The server is running smoothly 🚀",
        "model_loaded": True,
        "uptime_seconds": uptime
    })


# -------------------------------------------------------------
# 🏁 Application Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    print(Fore.MAGENTA + "\n🌍 Server running at: http://127.0.0.1:5000" + Style.RESET_ALL)
    app.run(debug=True, host='0.0.0.0', port=5000)
