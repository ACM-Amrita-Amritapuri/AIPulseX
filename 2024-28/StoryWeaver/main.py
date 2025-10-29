import os
import warnings
import asyncio

# Suppress TensorFlow warnings and messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress INFO and WARNING messages
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Turn off oneDNN optimizations
warnings.filterwarnings('ignore')

from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask,request,jsonify,send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model
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

'''Creating the function to process the given text and generate the story'''

# Creating the story generation function

async def generate_story(prompt):
    
    def clean_data(text):
        text=str(text).lower()
        text=''.join([i for i in text if i not in string.punctuation])
        text=text.encode('utf8').decode('ascii','ignore')
        return text
    
    next_words=50
    # Generate the next sequence of words
    for _ in range(next_words):
         # Step 1: Convert the current text into token sequences
         # The 'clean_data' function preprocesses the text (lowercase, remove punctuation, etc.)
        tokens = tokenizer.texts_to_sequences([clean_data(text=text)])[0]
        # If no valid tokens are found (e.g., text is empty or contains unknown words), stop generation
        if not tokens:
            break
        # Step 2: Keep only the last (max_sequence_length - 1) tokens
        # This ensures the input sequence length matches the model’s expected input size
        tokens = tokens[-(max_sequence_length - 1):]
        # Step 3: Pad the sequence so it has a uniform length for the model
        # Padding is added to the left ('pre') if the sequence is shorter than the required length
        tokens = pad_sequences([tokens], maxlen=max_sequence_length, padding='pre')
        # Step 4: Predict the next word probabilities using the trained model
        prediction = model.predict(tokens, verbose=0)
        # Step 5: Apply temperature scaling to control randomness
        # A lower temperature (<1) makes predictions more deterministic
        # A higher temperature (>1) makes them more random and creative
        # Add randomness by using temperature sampling
        temperature = 0.7
        prediction = prediction[0] / temperature
        prediction = np.exp(prediction) / np.sum(np.exp(prediction))
        # Step 6: Randomly sample the next word index based on the probability distribution
        # This avoids always picking the most probable word (adds natural variation)
        # Sample from the distribution instead of taking max
        predicted_index = np.random.choice(len(prediction), p=prediction)
        
        output = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted_index:
                output = word
                break
        
        if output:
            prompt += ' ' + output
            
            # Stop if we get punctuation or very long text
            if output in ['.', '!', '?'] or len(prompt.split()) > 100:
                break
        else:
            break
    
    return prompt.title()

def handler(prompt):
    # WRONG: nested asyncio.run may explode in notebooks/ASGI
    result = asyncio.run(generate_story(prompt))
    return result

'''Creating the main flask app''' 


app=Flask(__name__,static_folder='frontend',static_url_path='')
CORS(app)


'''Displaying the ui'''
@app.route('/')
def index():
    return send_from_directory('frontend','index.html')
@app.route('/style.css')
def serve_css():
    return send_from_directory('frontend', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('frontend', 'script.js')

'''Generating the story and returning it to the ui'''
@app.route('/generate',methods=['POST'])
def give_response():
    
    try:
        data=request.get_json()
        
        seed=data.get("seed_text").strip().lower()
        next_words=data.get('next_words',50) 
        
        if not seed:
            return jsonify({"error":"Seed text is required for story generation"}),400
        
        story=handler(text=seed,next_words=next_words)
        
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
        

if __name__=="__main__":
    print("The server is running at: http://127.0.0.1:5000")
    app.run(debug=True,host='0.0.0.0',port=5000)