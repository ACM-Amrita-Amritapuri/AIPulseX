import cv2
import face_recognition
import pickle
import os
import pandas as pd
from datetime import datetime
from sklearn import neighbors
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Parameters
model = "hog"  # Switch to HOG for CPU-friendly face detection
knn_neighbors = 3  # Number of neighbors for KNN
unknown_threshold = 0.5  # Threshold for identifying unknown faces
attendance_file = 'attendance.xlsx'
required_identifications = 3  # Number of correct identifications needed

# Load encodings and names from a file
with open('encodings.pkl', 'rb') as f:
    encodings, names = pickle.load(f)

# Train a KNN classifier
X_train, X_test, y_train, y_test = train_test_split(encodings, names, test_size=0.25, random_state=42)
knn_clf = neighbors.KNeighborsClassifier(n_neighbors=knn_neighbors, algorithm='ball_tree', weights='distance')
knn_clf.fit(X_train, y_train)

# Evaluate model on test set
y_pred = knn_clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy on test set: {accuracy:.2f}')

# Load or create the attendance Excel file
if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=['Roll Number', 'Date', 'Time', 'Days'])
    df.to_excel(attendance_file, index=False)
else:
    df = pd.read_excel(attendance_file)

# Real-time recognition with webcam or video
video_capture = cv2.VideoCapture(0)

frame_count = 0  # Initialize frame counter
identification_counts = {}  # Dictionary to store identification counts

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 2 != 0:  # Process every other frame
        continue

    rgb_frame = frame[:, :, ::-1]  # Convert to RGB
    face_locations = face_recognition.face_locations(rgb_frame, model=model)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Find the best match for the face
        distances, indices = knn_clf.kneighbors([face_encoding], n_neighbors=knn_neighbors)
        name = "Unknown"

        # Check if the closest known face is within the threshold
        if distances[0][0] < unknown_threshold:
            name = knn_clf.predict([face_encoding])[0]

            # Increment identification count
            if name in identification_counts:
                identification_counts[name] += 1
            else:
                identification_counts[name] = 1

            # Mark attendance if identified more than 3 times
            if identification_counts[name] >= required_identifications:
                current_date = datetime.now().date()
                already_marked = df[(df['Roll Number'] == name) & (df['Date'] == str(current_date))]

                if already_marked.empty:
                    current_time = datetime.now().strftime('%H:%M:%S')

                    # Check if the person already has a "Days" count
                    if not df[df['Roll Number'] == name].empty:
                        df.loc[df['Roll Number'] == name, 'Days'] += 1
                    else:
                        df = df.append({'Roll Number': name, 'Date': str(current_date), 'Time': current_time, 'Days': 1}, ignore_index=True)

                    # Update the attendance file
                    df.to_excel(attendance_file, index=False)
                    print(f'Attendance marked for {name} at {current_time} on {current_date}')
                identification_counts[name] = 0  # Reset after marking

        # Draw rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    # Press 'Esc' to quit
    if cv2.waitKey(1) & 0xFF == 27:
        break

video_capture.release()
cv2.destroyAllWindows()
