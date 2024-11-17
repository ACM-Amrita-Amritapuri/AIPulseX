import os
import cv2
import numpy as np
from keras.applications import MobileNetV2
from keras.applications.mobilenet_v2 import preprocess_input
from keras.preprocessing import image
from keras.models import Model
from mtcnn import MTCNN
import tkinter as tk
from tkinter import simpledialog
import time
import threading

base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
model = Model(inputs=base_model.input, outputs=base_model.output)

def extract_features(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
    except Exception as e:
        print(f"Error loading image {img_path}: {e}")
        return None
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    features = model.predict(img_data)
    features = features.flatten()
    features = features / np.linalg.norm(features)
    return features

def extract_features_from_frame(face_image):
    img = cv2.resize(face_image, (224, 224))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    features = model.predict(img)
    features = features.flatten()
    features = features / np.linalg.norm(features)
    return features

def build_encodings(known_faces_dir='known_faces', encodings_dir='encodings'):
    if not os.path.exists(encodings_dir):
        os.makedirs(encodings_dir)
    
    for person_name in os.listdir(known_faces_dir):
        person_dir = os.path.join(known_faces_dir, person_name)
        if not os.path.isdir(person_dir):
            continue
        person_encodings_dir = os.path.join(encodings_dir, person_name)
        if not os.path.exists(person_encodings_dir):
            os.makedirs(person_encodings_dir)
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            features = extract_features(img_path)
            if features is not None:
                encoding_filename = os.path.splitext(img_name)[0] + '.npy'
                encoding_path = os.path.join(person_encodings_dir, encoding_filename)
                np.save(encoding_path, features)
        print(f"Encodings for {person_name} saved.")

def prompt_user_for_name():
    def get_name():
        root = tk.Tk()
        root.withdraw()
        user_input = simpledialog.askstring(title="New Face Detected",
                                            prompt="Enter the name for the new face:")
        root.destroy()
        nonlocal name
        name = user_input

    name = None
    thread = threading.Thread(target=get_name)
    thread.start()
    thread.join()
    return name

def load_known_encodings(encodings_dir='encodings'):
    encodings = {}
    for person_name in os.listdir(encodings_dir):
        person_dir = os.path.join(encodings_dir, person_name)
        if not os.path.isdir(person_dir):
            continue
        encodings[person_name] = []
        for file in os.listdir(person_dir):
            if file.endswith('.npy'):
                encoding = np.load(os.path.join(person_dir, file))
                encodings[person_name].append(encoding)
    return encodings

def recognize_face(face_encoding, known_encodings, threshold=0.75):
    min_dist = float('inf')
    identity = "Unknown"
    for name, encodings in known_encodings.items():
        if len(encodings) == 0:
            continue
        encodings_np = np.array(encodings)
        distances = np.linalg.norm(encodings_np - face_encoding, axis=1)
        min_distance = np.min(distances)
        if min_distance < min_dist and min_distance < threshold:
            min_dist = min_distance
            identity = name
    return identity

def main():
    known_faces_dir = 'known_faces'
    encodings_dir = 'encodings'
    unknown_faces_dir = 'unknown_faces'

    for directory in [known_faces_dir, encodings_dir, unknown_faces_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    build_encodings(known_faces_dir, encodings_dir)
    known_encodings = load_known_encodings(encodings_dir)
    print(f"Loaded encodings for {len(known_encodings)} people.")

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Could not open video stream.")
        return

    detector = MTCNN()
    unknown_faces = []
    MAX_FRAMES = 20
    frame_count = 0
    SKIP_FRAMES = 2
    print("Starting video stream. Press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame.")
            break

        frame_count += 1
        if frame_count % SKIP_FRAMES != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = detector.detect_faces(rgb_frame)
        faces = []
        for detection in detections:
            x, y, w, h = detection['box']
            x, y = max(0, x), max(0, y)
            faces.append((x, y, w, h))

        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            face_encoding = extract_features_from_frame(face_img)
            if face_encoding is None:
                continue

            name = recognize_face(face_encoding, known_encodings)

            if name == "Unknown":
                unknown_faces.append(face_img)
                if len(unknown_faces) >= MAX_FRAMES:
                    timestamp = int(time.time())
                    for idx, img in enumerate(unknown_faces):
                        img_path = os.path.join(unknown_faces_dir, f"unknown_{timestamp}_{idx}.jpg")
                        cv2.imwrite(img_path, img)
                    
                    print("Unknown face detected. Prompting for label...")
                    person_name = prompt_user_for_name()
                    
                    if person_name:
                        person_dir = os.path.join(known_faces_dir, person_name)
                        if not os.path.exists(person_dir):
                            os.makedirs(person_dir)
                        
                        for img_name in os.listdir(unknown_faces_dir):
                            if img_name.startswith(f"unknown_{timestamp}_"):
                                src_path = os.path.join(unknown_faces_dir, img_name)
                                dest_path = os.path.join(person_dir, img_name.replace(f"unknown_{timestamp}_", ""))
                                os.rename(src_path, dest_path)
                        
                        build_encodings(known_faces_dir, encodings_dir)
                        known_encodings = load_known_encodings(encodings_dir)
                        print(f"Added {person_name} to known faces.")
                    else:
                        print("No name entered. Unknown face not added.")
                    
                    unknown_faces = []
            
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.rectangle(frame, (x, y-30), (x+w, y), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (x+5, y-10), font, 0.8, (255, 255, 255), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
