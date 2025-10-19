# StoryWeaver
### AI-Powered Story Generation with LSTM Neural Networks

---

## Overview

**StoryWeaver** is an intelligent story generation application that transforms simple prompts into engaging narratives using deep learning. Powered by a 2-layer LSTM (Long Short-Term Memory) neural network, this application takes user input as a story opening and generates creative continuations with natural language flow.

### Key Features
- **AI-Powered Generation**: Advanced LSTM model for coherent story creation
- **Interactive Web Interface**: Clean, responsive UI with dark/light mode toggle
- **Real-time Processing**: Instant story generation with temperature-based sampling

## Technology Stack

### Backend
- **Flask**
- **TensorFlow/Keras**

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript**

### Machine Learning
- **LSTM Neural Network**
- **Text Preprocessing**

## Model Architecture

The StoryWeaver uses a 2-layer LSTM (Long Short-Term Memory) neural network for text generation.

### Architecture Visualization

```
User Input: "Once upon a time"
                ↓
        [ Text Preprocessing ]
        - Cleaning & Tokenization
        - Sequence Padding
                ↓
    ╔═══════════════════════╗
    ║     Input Layer       ║
    ║   (Max Length: 60)    ║
    ╚═══════════════════════╝
                ↓
    ╔═══════════════════════╗
    ║    LSTM Layer 1       ║
    ║   (First Recurrent)   ║
    ╚═══════════════════════╝
                ↓
    ╔═══════════════════════╗
    ║    LSTM Layer 2       ║
    ║   (Second Recurrent)  ║
    ╚═══════════════════════╝
                ↓
    ╔═══════════════════════╗
    ║    Dense Output       ║
    ║   (Softmax Activation)║
    ╚═══════════════════════╝
                ↓
        [ Word Prediction ]
                ↓
Output: "Once upon a time there was a magical kingdom..."
```

### Generation Process
1. **Input Processing**: User prompt is cleaned and tokenized
2. **Sequence Preparation**: Text is converted to numerical sequences with padding
3. **Prediction**: Model predicts the next most likely word
4. **Iteration**: Process repeats until approximately 50 words are generated
5. **Output**: Complete story is returned and displayed in the browser

### Model Parameters
- **Maximum Sequence Length**: 60 tokens
- **Generation Limit**: ~50 words per story
- **Vocabulary**: Based on training dataset tokenization

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Git (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd StoryWeaver
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install using uv (recommended)
pip install uv
uv sync

# OR install using pip
pip install flask flask-cors tensorflow numpy pandas scikit-learn
```

### Step 4: Verify Model Files
Ensure the following files exist in the `Models/` directory:
- `best_story_model.keras` (Pre-trained LSTM model)
- `tokenizer.pickle` (Text tokenizer)

### Step 5: Run the Application
```bash
python main.py
```

### Step 6: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### Project Structure
```
StoryWeaver/
├── main.py              # Flask application entry point
├── pyproject.toml       # Project dependencies
├── uv.lock             # Dependency lock file
├── frontend/            # Web interface files
│   ├── index.html       # Main HTML page
│   ├── style.css        # Styling
│   └── script.js        # JavaScript functionality
└── Models/              # Pre-trained model files
    ├── best_story_model.keras  # LSTM model
    └── tokenizer.pickle        # Text tokenizer
```

## Usage

### API Endpoints
- **GET** `/` - Serves the main web interface
- **POST** `/generate` - Generates story from input text
  ```json
  {
    "seed_text": "Your story opening here"
  }
  ```
- **GET** `/health` - Health check endpoint

## Contact

**Developer**: Nishanth Devabathini  
**Email**: dn8.porps@gmail.com  
**LinkedIn**: [https://www.linkedin.com/in/nishanth-devabathini-738a8a212/](https://www.linkedin.com/in/nishanth-devabathini-738a8a212/)
