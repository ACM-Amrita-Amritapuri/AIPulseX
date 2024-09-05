# Face Swapping with OpenCV, Mediapipe, and Delaunay Triangulation

This project demonstrates how to perform face swapping between two images using OpenCV, Mediapipe, and Delaunay triangulation. The process involves detecting facial landmarks, applying Delaunay triangulation to the face, and seamlessly blending the swapped face onto the target image.

## Requirements

Before running the code, ensure you have the following dependencies installed:

- Python 3.10
- OpenCV (`cv2`)
- Mediapipe (`mediapipe`)
- NumPy (`numpy`)
- Matplotlib (`matplotlib`)
- Pandas (`pandas`)

You can install these dependencies using pip:

```bash
pip install opencv-python mediapipe numpy matplotlib pandas
```

## Project Structure

- `main.ipynb`: The main script that performs face swapping between two images.
- `image1.jpg`: The source image from which the face will be swapped.
- `image2.jpeg`: The target image onto which the face will be swapped.
- `README.md`: This file, which explains how the project works and how to run it.

## How It Works

1. **Face Detection and Landmark Extraction**:
   - The script reads the input images using OpenCV.
   - Mediapipe's FaceMesh model is used to detect facial landmarks for both images.

2. **Delaunay Triangulation**:
   - The facial landmarks are used to create a Delaunay triangulation, dividing the face into small triangles.
   - The triangulation ensures that the face structure is maintained during the face swap.

3. **Warping Triangles**:
   - Each triangle from the source face is warped to match the corresponding triangle on the target face.
   - The warped triangles are blended together to form the new face.

4. **Seamless Cloning**:
   - The new face is blended onto the target image using OpenCV's `seamlessClone` function, ensuring smooth edges and natural appearance.

## Running the Script

To run the face swap, simply execute the `face_swap.py` script:

```bash
python face_swap.py
```

This will generate a final image with the swapped face, displayed using Matplotlib.

## Output

The final result is a seamless face swap, where the face from `image1.jpg` is transferred to `image2.jpeg`. The output image is displayed using Matplotlib.

## Notes

- Ensure that the input images have faces that are clearly visible and facing forward for best results.
- The script is designed for educational purposes and might require fine-tuning for specific use cases.

