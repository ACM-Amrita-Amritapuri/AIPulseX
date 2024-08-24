import cv2
from matplotlib import pyplot as plt

def face_detect (image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
    for i, (x, y, w, h) in enumerate(faces):
        face_image = image[y:y+h, x:x+w]
        filename = f"face_{i}.jpg"
        cv2.imwrite(filename, face_image)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return image

image = cv2.imread('img.jpg')  # IMAGE FILE NAME NEED TO BE UPDATED
ans = face_detect(image)
plt.imshow(ans)
plt.title('FCES DETECTED')
plt.show()