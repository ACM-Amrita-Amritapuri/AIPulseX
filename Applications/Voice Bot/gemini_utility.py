import os
import json

import google.generativeai as genai

working_directory = os.path.dirname(os.path.abspath(__file__))

config_file_path = f"{working_directory}/config.json"
config_data = json.load(open(config_file_path))
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

def load_gemini_pro_model():
    gemini_pro_model = genai.GenerativeModel("gemini-pro")
    return gemini_pro_model

