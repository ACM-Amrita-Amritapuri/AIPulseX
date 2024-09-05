import face_recognition
import os
import pickle
import cv2

# Directories for known faces
KNOWN_FACES_DIR = 'known_faces'

# Lists to hold encodings and names
encodings = []
names = []

# Load known faces and augment data
def augment_image(image):
    """Apply transformations to augment the image."""
    augmented_images = [image]
    flip = cv2.flip(image, 1)  # Horizontal flip
    augmented_images.append(flip)
    return augmented_images

for roll_number in os.listdir(KNOWN_FACES_DIR):
    roll_dir = os.path.join(KNOWN_FACES_DIR, roll_number)
    for filename in os.listdir(roll_dir):
        image_path = os.path.join(roll_dir, filename)
        if os.path.isfile(image_path):
            image = face_recognition.load_image_file(image_path)
            for aug_image in augment_image(image):
                face_enc = face_recognition.face_encodings(aug_image)
                if face_enc:
                    encodings.append(face_enc[0])
                    names.append(roll_number)

# Save encodings and names to a file
with open('encodings.pkl', 'wb') as f:
    pickle.dump((encodings, names), f)

print("Encodings have been precomputed and saved.")
