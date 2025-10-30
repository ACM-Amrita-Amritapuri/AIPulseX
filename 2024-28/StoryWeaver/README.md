# StoryWeaver

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-Flask-red.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)

AI-Powered Story Generation with a 2-Layer LSTM Neural Network. Transform a simple prompt into an engaging narrative.

---

## 🎬 Demo

![StoryWeaver Demo GIF]

## ✨ Overview

**StoryWeaver** is an intelligent story generation application that transforms simple prompts into engaging narratives using deep learning. Powered by a 2-layer LSTM (Long Short-Term Memory) neural network, this application takes a user's story opening and generates creative, natural-sounding continuations.

### Key Features
-   🤖 **AI-Powered Generation**: A 2-Layer LSTM model generates coherent and creative story continuations.
-   🌐 **Interactive Web Interface**: A clean, responsive UI built with HTML, CSS, and vanilla JavaScript.
-   ⚡ **Real-time Processing**: Generates ~50 words of text instantly, using temperature-based sampling for creative results.
-   🌗 **Dark/Light Mode**: Includes a theme-toggle for user comfort.

## 🛠️ Technology Stack

| Area | Technology |
| :--- | :--- |
| **Backend** | Flask, Flask-CORS, TensorFlow/Keras |
| **Frontend** | HTML5, CSS3, JavaScript |
| **ML/Data** | NumPy, Pandas, Scikit-learn, Pickle |
| **Python Env** | `uv` (or `pip`), `venv` |

## 🧠 Model Architecture

The core of StoryWeaver is a 2-layer LSTM (Long Short-Term Memory) neural network.



### Generation Flow
The generation process is iterative. The model's output is fed back as its new input, allowing it to write word by word.

```

User Input: "Once upon a time"
↓
[ Text Preprocessing ]

  - Cleaning & Tokenization
  - Sequence Padding (to 60 tokens)
    ↓
    ╔═══════════════════════╗
    ║   Embedding Layer     ║
    ╚═══════════════════════╝
    ↓
    ╔═══════════════════════╗
    ║    LSTM Layer 1       ║
    ╚═══════════════════════╝
    ↓
    ╔═══════════════════════╗
    ║    LSTM Layer 2       ║
    ╚═══════════════════════╝
    ↓
    ╔═══════════════════════╗
    ║    Dense Output       ║
    ║  (Softmax Activation) ║
    ╚═══════════════════════╝
    ↓
    [ Word Prediction ] (e.g., "there")
    ↓
    New Input: "Once upon a time there"
    ↓
    [ Process Repeats 50 times... ]
    ↓
    Output: "Once upon a time there was a magical kingdom..."

<!-- end list -->

````

### Model Parameters
-   **Maximum Sequence Length**: 60 tokens
-   **Generation Limit**: ~50 words per request
-   **(Add Vocabulary Size)**: e.g., 8,672 tokens
-   **(Add Training Data info)**: e.g., "Trained on a dataset of 20,000 short fantasy stories."

## 📦 Installation & Setup

### Prerequisites
-   Python 3.11 or higher
-   Git

### Step 1: Clone the Repository
```bash
git clone [https://github.com/your-username/StoryWeaver.git](https://github.com/your-username/StoryWeaver.git)
cd StoryWeaver
````

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

This project uses `uv` for fast dependency management.

```bash
# Install uv (if you don't have it)
pip install uv

# Sync with the lock file
uv sync
```

**Alternatively, using `pip`:**

```bash
# Install dependencies from pyproject.toml
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
**`http://127.0.0.1:5000`**

-----

## Usage

### Web Interface

Navigate to **`http://127.0.0.1:5000`**, type your story prompt, and click "Generate."

### API Endpoints

You can also interact with the API directly.

#### `POST /generate`

Generates a story continuation.
**Body:**

```json
{
  "prompt": "Your story opening here"
}
```

*(Note: Your original README listed `"seed_text"`. Please ensure your `main.py` is looking for `"prompt"` as used in this example, or change this example to match your code.)*

**`curl` Example:**

```bash
curl -X POST [http://127.0.0.1:5000/generate](http://127.0.0.1:5000/generate) \
-H "Content-Type: application/json" \
-d '{"prompt":"The old castle was silent"}'
```

**Success Response:**

```json
{
  "story": "The old castle was silent and the air was cold he walked down the empty hall and saw a light..."
}
```

#### `GET /health`

A simple health check endpoint.

```bash
curl [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)
```

**Response:** `{"status": "ok"}`

## 📁 Project Structure

```
StoryWeaver/
├── main.py             # Flask application entry point
├── pyproject.toml      # Project dependencies
├── uv.lock             # Dependency lock file
├── frontend/
│   ├── index.html      # Main HTML page
│   ├── style.css       # Styling
│   └── script.js       # JavaScript functionality
└── Models/
    ├── best_story_model.keras  # LSTM model
    └── tokenizer.pickle        # Text tokenizer
```

## 🤝 Contributing

Contributions are welcome\! If you'd like to improve StoryWeaver, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## 📬 Contact

**Nishanth Devabathini**

  - **Email**: `dn8.porps@gmail.com`
  - **LinkedIn**: [https://www.linkedin.com/in/nishanth-devabathini-738a8a212/](https://www.linkedin.com/in/nishanth-devabathini-738a8a212/)

<!-- end list -->

```
```
