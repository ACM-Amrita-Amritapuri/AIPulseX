### **MCQ-GENERATOR**

The MCQ Generator is implemented in Python using the Flask framework. The application provides an interface for users to upload documents and generates multiple-choice questions (MCQs) based on the content of those documents. Below is a breakdown of the key components and functionality of the code:

### 1. **Main Application (app.py)**

- **Flask Setup**: The application is initialized using Flask, and configurations for uploading files and saving results are defined.
  
- **Allowed File Types**: The app restricts uploads to specific file types: PDF, TXT, and DOCX.

- **File Handling**:
  - The `allowed_file()` function checks if the uploaded file is of a valid type.
  - The `extract_text_from_file()` function uses different libraries to extract text based on the file type:
    - **PDF**: Uses `pdfplumber` to read and extract text from PDF files.
    - **DOCX**: Uses `python-docx` to extract text from Word documents.
    - **TXT**: Reads the content directly from text files.

- **MCQ Generation**:
  - The `Question_mcqs_generator()` function formulates a prompt for the Google Generative AI model to generate MCQs from the extracted text. The model outputs a structured format of questions, options, and the correct answer.
  
- **File Saving**:
  - The `save_mcqs_to_file()` function saves the generated MCQs in a text file.
  - The `create_pdf()` function creates a PDF file using the `FPDF` library, formatting the MCQs for better presentation.

### 2. **Web Routes**:

- **Home Route (`/`)**: Renders the main upload form where users can select files and specify the number of questions they want to generate.

- **Generate Route (`/generate`)**: Handles the file upload and processes the request to generate MCQs. It checks for the uploaded file, extracts the text, and invokes the MCQ generation function. After generation, it saves the results and renders them on a results page.

- **Download Route (`/download/<filename>`)**: Facilitates downloading the generated MCQs in either TXT or PDF format.

### 3. **HTML Templates**:

- **index.html**: The main page where users can upload documents and enter the desired number of questions. It features a clean and responsive design.

- **results.html**: Displays the generated MCQs along with options to download the results. It uses a styled layout to present each question and its options clearly.

### 4. **Environment Setup**:

- The application requires setting an API key for Google Generative AI, which is crucial for generating MCQs.
  
- The application creates necessary directories for uploads and results if they do not exist.

### 5. **Dependencies**:

The project uses several external libraries, including Flask for the web framework, pdfplumber for PDF handling, python-docx for Word documents, and FPDF for PDF generation.


This code structure provides a comprehensive and user-friendly tool for generating MCQs from textual documents, leveraging modern AI capabilities to assist in educational contexts.

