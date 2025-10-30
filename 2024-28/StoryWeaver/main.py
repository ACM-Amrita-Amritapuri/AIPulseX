import os
import warnings
import asyncio

# Suppress TensorFlow warnings and messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress INFO and WARNING messages
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Turn off oneDNN optimizations
warnings.filterwarnings('ignore')

from tensorflow.keras.preprocessing.sequence import pad_sequences #type: ignore
from flask import Flask,request,jsonify,send_from_directory #type: ignore
from flask_cors import CORS
from tensorflow.keras.models import load_model #type: ignore
import numpy as np 
import pickle 
import traceback 
import string

# Declaring the constants

MODEL_PATH=r'Models\best_story_model.keras'
TOKENIZER_NAME=r'Models\tokenizer.pickle'
max_sequence_length=60


'''Loading the model , tokenizer and model parameters'''

# Loading model
model=load_model(MODEL_PATH)

# Loading tokenizer and Model parameters 

with open(TOKENIZER_NAME,'rb') as f:
    tokenizer=pickle.load(f)    

print(f"Model loaded with max sequence length: {max_sequence_length}")

# Build reverse index for faster word lookup
index_to_word = {index: word for word, index in tokenizer.word_index.items()}

def clean_data(text):
    """Preprocess text by lowercasing, removing punctuation, and handling encoding."""
    text = str(text).lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    text = text.encode('utf8').decode('ascii', 'ignore')
    return text

def generate_story(prompt, next_words=50, temperature=0.7, max_words=100):
    """Generate story continuation from prompt using the trained model."""
    
    if not prompt or not prompt.strip():
        return "Error: Empty prompt provided."
    
    for _ in range(next_words):
        cleaned_prompt = clean_data(prompt)
        tokens = tokenizer.texts_to_sequences([cleaned_prompt])[0]
        
        if not tokens:
            break
        
        tokens = tokens[-(max_sequence_length - 1):]
        tokens = pad_sequences([tokens], maxlen=max_sequence_length, padding='pre')
        
        prediction = model.predict(tokens, verbose=0)[0]
        prediction = np.exp(prediction / temperature) / np.sum(np.exp(prediction / temperature))
        
        predicted_index = np.random.choice(len(prediction), p=prediction)
        output = index_to_word.get(predicted_index, "")
        
        if output:
            prompt += ' ' + output
            if output in ['.', '!', '?'] or len(prompt.split()) > max_words:
                break
        else:
            break
    
    return prompt.title()

def handler(prompt):
    """Lightweight wrapper around generate_story with basic validation."""
    text = (prompt or "").strip()
    if not text:
        return "Error: Empty prompt provided."
    return generate_story(text)

'''Creating the main flask app''' 


app=Flask(__name__,static_folder='frontend',static_url_path='')
CORS(app)


# -------------------------------------------------------------
# Displaying the UI (Frontend)
# -------------------------------------------------------------

@app.route('/')
def index():
    """
    Route: '/'
    Purpose: Serves the main HTML file of the frontend.
    This function sends the 'index.html' file located in the 'frontend' directory.
    """
    return send_from_directory('frontend', 'index.html')


@app.route('/style.css')
def serve_css():
    """
    Route: '/style.css'
    Purpose: Serves the CSS stylesheet for the frontend.
    This ensures the webpage has proper styling when loaded in the browser.
    """
    return send_from_directory('frontend', 'style.css')


@app.route('/script.js')
def serve_js():
    """
    Route: '/script.js'
    Purpose: Serves the JavaScript file for the frontend.
    This script handles user interactions and API calls to the backend.
    """
    return send_from_directory('frontend', 'script.js')


# Generating the story and returning it to the UI
@app.route('/generate', methods=['POST'])
def give_response():
    """
    Route: '/generate'
    Method: POST
    Purpose: Handles incoming text prompts from the frontend UI and 
             generates a story or continuation using the trained model.
    Steps typically performed (to be added inside this function):
        1. Receive user input (prompt) from frontend via POST request.
        2. Process the input
        3. Generate predicted text using a trained model.
        4. Return the generated story as JSON to the frontend.
    """
    
    pass

    
    try:
        data=request.get_json()
        
        seed=data.get("seed_text").strip().lower()
        next_words=data.get('next_words',50) 
        
        if not seed:
            return jsonify({"error":"Seed text is required for story generation"}),400
        
        story = handler(seed)
        
        return jsonify({"story":story}),200
    except Exception as e:
        print(f"An error occured: {e}")
        traceback.print_exc()
        return jsonify({"error":"An error occured during story generation"}),500

@app.route('/health',methods=['GET'])
def check_health():
    return jsonify ({
        "status":"ok",
        "message":"The server is running "
        })
        


# -------------------------------------------------------------
# 🚀 Application Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    print("\n Server is running at: http://127.0.0.1:5000\n")
    
    # Start the Flask development server
    # debug=True enables auto-reload and detailed error pages
    # host='0.0.0.0' allows access from other devices on the same network
    app.run(debug=True, host='0.0.0.0', port=5000)
