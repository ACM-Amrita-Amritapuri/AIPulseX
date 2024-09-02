import cv2
import mediapipe as mp
import math
import time

#Hand
class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon 

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon, 
            min_tracking_confidence=self.minTrackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

        self.swipe_ended = False
        self.swipe_started = False
        self.lswipe_ended = False
        self.lswipe_started = False
        self.zoom_started = False
        self.zoom_ended = False
        self.zout_started = False
        self.zout_ended = False
        self.left_threshold = 400
        self.right_threshold = 270
        self.start_time = 0

    def findHands(self, img, draw=True, flipType=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(
                self.results.multi_handedness, self.results.multi_hand_landmarks
            ):
                myHand = {}
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)

                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS
                    )

        if draw:
            return allHands, img
        else:
            return allHands, img

    def fingersUp(self, myHand):
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        fingers = []

        if myHandType == "Right":
            if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                fingers.append(1)
            else:
                fingers.append(0)

        for id in range(1, 5):
            if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self, p1, p2, img=None):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            return length, info, img
        else:
            return length, info

    async def gestureControl(self, img):
        hands, img = self.findHands(img)
        h, w, _ = img.shape  # get the dimensions of the image
        left_corner_threshold = w // 5  # define left corner threshold as 1/5th of the width
        right_corner_threshold = 4 * w // 5

        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]
            handType1 = hand1["type"]

            fingers1 = self.fingersUp(hand1)

            # Zoom In Gesture
            if (
                fingers1[0]
                and fingers1[1]
                and not fingers1[2]
                and not fingers1[3]
                and not fingers1[4]
            ):
                length, info, _ = self.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)
                if not self.zoom_started and length < 50:
                    self.zoom_started = True
                if self.zoom_started and length > 120:
                    self.zoom_started = False
                    self.zoom_ended = True
                if self.zoom_ended:
                    self.zoom_ended = False
                    print("Zoomed")
                    return "zi"

            # Zoom Out Gesture
            if (
                fingers1[0]
                and fingers1[1]
                and fingers1[2]
                and not fingers1[3]
                and not fingers1[4]
            ):
                length, info, _ = self.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)
                if not self.zout_started and length > 120:
                    self.zout_started = True
                if self.zout_started and length < 50:
                    self.zout_started = False
                    self.zout_ended = True
                if self.zout_ended:
                    self.zout_ended = False
                    print("Zoomed Out")
                    return "zo"

            # Right Swipe Gesture
            if fingers1[1] and fingers1[2] and fingers1[3] and fingers1[4]:
                indMid = [lmList1[8][0], lmList1[12][0], lmList1[16][0], lmList1[16][0]]
                if not self.swipe_started and max(indMid) > self.left_threshold:
                    self.swipe_started = True
                if self.swipe_started and min(indMid) < self.right_threshold:
                    self.swipe_started = False
                    self.swipe_ended = True
                if self.swipe_ended:
                    print("Swipe detected!")
                    # return "rs"
                    self.swipe_ended = False
                    return "rs"

            # Left Swipe Gesture
            if fingers1[1] and fingers1[2] and fingers1[3] and not fingers1[4]:
                indMid = [lmList1[8][0], lmList1[12][0], lmList1[16][0], lmList1[16][0]]
                if not self.lswipe_started and min(indMid) < self.right_threshold:
                    self.lswipe_started = True
                if self.lswipe_started and max(indMid) > self.left_threshold:
                    self.lswipe_started = False
                    self.lswipe_ended = True
                if self.lswipe_ended:
                    print("Left Swipe detected!")
                    # return "ls"
                    self.lswipe_ended = False
                    return "ls"

            # scroll down
            if not fingers1[0] and fingers1[1] and fingers1[2] and not fingers1[3] and not fingers1[4]:
                # index position
                indextip = lmList1[8][0]
                if indextip < left_corner_threshold:
                    print("Scroll down")
                    return "sd"

            # scroll up
            if not fingers1[0] and fingers1[1] and fingers1[2] and not fingers1[3] and not fingers1[4]:
                # index position
                indextip = lmList1[8][0]
                if indextip > right_corner_threshold:
                    print("Scroll up")
                    return "su"

            # Exit Gesture (All Fingers Up)
            if all(fingers1):
                if self.start_time == 0:
                    self.start_time = time.time()
                current_time = time.time()
                elapsed_time = current_time - self.start_time
                if elapsed_time >= 8:
                    print("Exiting...") 
                    exit()
        else:
            self.start_time = 0

        return 'hmm'

# def main():
#     cap = cv2.VideoCapture(0)
#     detector = HandDetector(detectionCon=0.8, maxHands=2)

#     while True:
#         success, img = cap.read()
#         img = cv2.flip(img, 1)
#         img = detector.gestureControl(img)

#         cv2.imshow("frame", img)
#         if cv2.waitKey(20) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()