import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image

# Load the pre-trained model and cluster centers
PROTOTXT = '/Users/sanjitteja/Desktop/Colorizing-black-and-white-images-using-Python-master/model/colorization_deploy_v2.prototxt'
POINTS = '/Users/sanjitteja/Desktop/Colorizing-black-and-white-images-using-Python-master/model/pts_in_hull.npy'
MODEL = '/Users/sanjitteja/Desktop/Colorizing-black-and-white-images-using-Python-master/model/colorization_release_v2.caffemodel'

net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
pts = np.load(POINTS)

class8 = net.getLayerId("class8_ab")
conv8 = net.getLayerId("conv8_313_rh")
pts = pts.transpose().reshape(2, 313, 1, 1)
net.getLayer(class8).blobs = [pts.astype("float32")]
net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

def colorize_image(image_path):
    image = cv2.imread(image_path)
    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)

    colorized = (255 * colorized).astype("uint8")
    return colorized

# Mention the image path here
image_path = '/Users/sanjitteja/Desktop/Colorizing-black-and-white-images-using-Python-master/IMG_20240629_125332.jpg'

# Process the image
colorized_img = colorize_image(image_path)

# Display the original and colorized images
original_img = Image.open(image_path)

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(original_img)
plt.axis('off')

plt.subplot(1, 2, 2)
plt.title("Colorized Image")
plt.imshow(cv2.cvtColor(colorized_img, cv2.COLOR_BGR2RGB))
plt.axis('off')

plt.show()
