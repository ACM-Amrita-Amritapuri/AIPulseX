# Chemical Buddy

**Chemical Buddy** is an AI-powered chemistry study assistant designed to help users with chemistry-related queries, document analysis, unit conversions, and image search. By integrating natural language processing, PDF processing, and image retrieval, it offers a comprehensive study tool to enhance learning.

## Table of Contents
- [Inspiration](#inspiration)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Challenges](#challenges)
- [Accomplishments](#accomplishments)
- [Future Plans](#future-plans)
- [Contributing](#contributing)

## Inspiration
The idea behind Chemical Buddy was to create an interactive and accessible tool for students and enthusiasts to easily access chemistry knowledge. The platform aims to provide a personalized learning experience through advanced AI, assisting users with queries, document extraction, and visual aids.

## Features
- **Ask Chemistry Questions**: Users can ask chemistry-related questions and receive detailed, context-rich answers.
- **PDF Upload**: Allows users to upload PDF documents, extract relevant text, and use the information to enrich responses.
- **Unit Conversion**: A built-in unit converter helps with common chemistry conversions like moles to grams.
- **Image Search**: Integrated with Google Custom Search API to retrieve relevant images for enhanced understanding.
- **Knowledge Base**: Includes informative articles on various chemistry topics for additional learning support.

## Tech Stack
- **Front-end**: Streamlit
- **Natural Language Processing**: Langchain, Google Generative AI
- **PDF Processing**: PyPDF2
- **Vector Search**: FAISS
- **Image Search**: Google Custom Search API

## Setup and Installation

To run the project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/chemical-buddy.git
   cd chemical-buddy
   ```

2. **Create a virtual environment**
   ```bash
   pip install opencv-python mediapipe numpy matplotlib pandas
   ```
3. **Install the required dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up API Keys**
   - paste your api keys in .env file
   - GOOGLE_API_KEY=your_google_api_key
     
5. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Usage
- Ask Questions: Enter your chemistry-related questions in the input box, and the AI will generate detailed responses.
- Upload PDFs: Upload a chemistry-related PDF, and the text will be processed for better understanding.
- Use Unit Converter: Input values to convert common chemistry units.
- Search Images: Input chemistry queries to retrieve relevant images from Google.

## Accomplishments
- Built an AI-powered chatbot that provides accurate chemistry answers.
- Developed a document upload feature for extracting and utilizing user PDFs.
- Created a clean, user-friendly interface that makes learning more accessible.
- Successfully integrated image search for enhanced visual learning.

## Future Plans

- Enhanced AI Capabilities: Further improve the AI's understanding of complex chemistry topics.
- Broader Topic Coverage: Expand into other branches of science.
- Interactive Learning: Add features like quizzes and flashcards to make learning more interactive.
- Mobile Application: Develop a mobile version to provide access to users on the go.
- Personalization: Implement user profiles and personalized learning experiences.

## Contributing

We welcome contributions! Feel free to open issues or submit pull requests to improve Chemical Buddy.

