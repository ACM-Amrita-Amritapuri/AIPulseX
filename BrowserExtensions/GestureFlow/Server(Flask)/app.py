import cv2
from flask import Flask, jsonify, request
import time
import threading
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from hand1 import HandDetector

app = Flask(__name__)

# Store data in memory for simplicity (use a database or message queue for production)
data_store = []
data_event = threading.Event()

detector = HandDetector()
last_action_time = 0
def data_url_to_image(data_url):
    # Split the data URL to get the base64 part
    header, base64_data = data_url.split(",", 1)
    
    # Decode the base64 data
    image_data = base64.b64decode(base64_data)
    
    # Create a BytesIO object from the image data
    image_stream = BytesIO(image_data)
    
    # Open the image using PIL (Pillow)
    image = Image.open(image_stream)
    
    return image

def pillow_image_to_opencv(pillow_image):
    # Convert Pillow image to a NumPy array
    image_np = np.array(pillow_image)
    
    # Convert RGB to BGR (OpenCV uses BGR by default)
    if image_np.ndim == 3 and image_np.shape[2] == 3:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    return image_np


@app.route('/poll')
def poll():
    def get_data():
        # Wait for new data or timeout
        if not data_event.wait(timeout=10):  # Wait up to 10 seconds
            return jsonify({'message': 'No new data'}), 204
        # Return new data
        data_event.clear()
        return jsonify(data_store.pop(0))
    
    return get_data()

@app.route('/send', methods=['POST'])
async def send():
    global last_action_time

    current_time = time.time()
    # if current_time - last_action_time < 1:
    #     return jsonify({'status': 'No action'}), 200
    data = request.json
    data_store.append(data)
    
    # Process the image data
    image = data_url_to_image(data)
    image_np = pillow_image_to_opencv(image)

    # Custom timestamp management
    action = await detector.gestureControl(image_np)

    data_event.set()
    return jsonify({'status': 'data received', 'action': action}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
