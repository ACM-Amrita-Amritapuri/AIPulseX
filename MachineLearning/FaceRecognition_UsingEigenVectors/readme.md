# **Face Recognition Using Eigen Vectors and Euclidean Distance**

### **Introduction 📘**

This project implements a basic face recognition technique using Eigen Vectors and Euclidean distance. By applying Singular Value Decomposition (SVD) for dimensionality reduction, the system recognizes faces based on the closest match between a test image and stored images. This method is a simple approach to face recognition, focusing on essential image processing and distance measurement.

### **Project Details 📊**

1. **Eigen Vectors:** Key to reducing the dimensions of image data while retaining essential features.
2. **SVD (Singular Value Decomposition):** Used to decompose and compress image data into a manageable size for analysis.
3. **Euclidean Distance:** The primary method for comparing the test image with stored images, identifying the closest match.
4. **Basic Implementation:** Designed to recognize faces by comparing reduced-dimension representations of images.

### **Challenges & Solutions**

- **Dimensionality Reduction:** Striking a balance between reducing dimensions and retaining enough information for accurate recognition.
  - **Solution:** Carefully tune the SVD process to ensure the least amount of information is lost.
- **Noise Sensitivity:** The model's performance may degrade with noisy data.
  - **Solution:** Implement basic noise reduction techniques; for more robust results, consider advanced filtering methods.

### **Conclusion 📝**

This project provides a simple yet effective approach to face recognition using basic machine learning concepts. While the method may struggle with noise and more complex datasets, it serves as a solid foundation for understanding how Eigen Vectors and Euclidean distances can be applied in face recognition. Future improvements can enhance accuracy and robustness.

### **Team 👥**

- **Lokesh Madan**
