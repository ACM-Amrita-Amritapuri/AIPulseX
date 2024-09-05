import cv2
import mediapipe as mp

class HandSwipeDetector:
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence)
        self.prev_wrist_x = None
        self.line_x = None

    def detect_swipe(self, frame):
        height, width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.line_x is None:
            self.line_x = width // 2

        frame = cv2.line(frame, (self.line_x, 0), (self.line_x, height), (255, 0, 0), 2)

        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark

                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                wrist_x = int(landmarks[self.mp_hands.HandLandmark.WRIST].x * width)
                wrist_y = int(landmarks[self.mp_hands.HandLandmark.WRIST].y * height)

                frame = cv2.circle(frame, (wrist_x, wrist_y), 10, (0, 255, 0), -1)

                if self.prev_wrist_x is not None:
                    if self.prev_wrist_x < self.line_x and wrist_x >= self.line_x:
                        print("Swipe right")
                        return "rs"
                    elif self.prev_wrist_x > self.line_x and wrist_x <= self.line_x:
                        print("Swipe left")
                        return "ls"

                self.prev_wrist_x = wrist_x

        return "no"

def main():
    detector = HandSwipeDetector()
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Detect swipe
        frame = detector.detect_swipe(frame)

        # Display the frame
        cv2.imshow('Hand Swipe Detection', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()
