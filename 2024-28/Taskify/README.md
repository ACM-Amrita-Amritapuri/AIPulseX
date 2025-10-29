# Taskify

A web app for generating personalized learning schedules. Upload PDFs or DOCX files, then use the chat interface to create week-by-week plans based on your materials.

Built with Flask, MongoDB, Pinecone, and Google Gemini.

## Setup

**Requirements:**
- Python 3.11+
- MongoDB
- Pinecone account with an existing index
- Google Gemini API key

**Installation (Windows PowerShell):**

```powershell
git clone <repository-url>
cd 2024-28/Taskify

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Create .env file with the following:
# SECRET_KEY=your-secret-key
# MONGODB_URI=mongodb://localhost:27017/
# DATABASE_NAME=Taskify
# COLLECTION_NAME=Users
# GOOGLE_API_KEY=your-google-api-key
# PINECONE_API_KEY=your-pinecone-api-key
# INDEX_NAME=your-pinecone-index-name
# GROQ_API_KEY=your-groq-api-key (optional)
# GROQ_MODEL=llama-3.3-70b-versatile (optional)

python app.py
```

Open http://127.0.0.1:5000

## Features

- User registration and login
- Upload PDF/DOCX files for processing
- Document search using Pinecone vector store
- Chat interface powered by Google Gemini
- Generate multi-week schedules from uploaded materials
- View activity logs

## Project Structure

```
Taskify/
├── app.py                  # Main Flask application
├── Backend/
│   ├── auth.py             # Authentication routes
│   ├── Schedule_gen.py     # Document upload and schedule generation
│   └── utils.py            # Vector store and LLM utilities
├── Frontend/
│   ├── Templates/          # HTML pages
│   └── scripts/            # CSS and JavaScript
├── requirements.txt
└── pyproject.toml
```

## Routes

**Authentication:**
- `GET/POST /register` - Create account
- `POST /login` - Login (returns JWT)
- `GET /logout` - Logout
- `GET/POST /change-password` - Change password

**Pages:**
- `GET /` - Landing page
- `GET /dashboard` - Main dashboard
- `GET /scheduler` - Schedule interface
- `GET /documents` - Document upload page
- `GET /my-documents` - View uploaded documents
- `GET /logs` - Application logs

**API:**
- `POST /Upload` - Upload and process documents
- `POST /scheduler/api/chat/message` - Send chat message
- `POST /scheduler/api/generate` - Generate schedule from input
- `POST /scheduler/api/generate-from-chat` - Generate schedule from chat history
- `GET /scheduler/api/schedules` - List all schedules
- `GET /scheduler/api/schedules/<id>` - Get specific schedule
- `DELETE /scheduler/api/schedules/<id>` - Delete schedule
- `GET /scheduler/api/chat/history` - Get chat history
- `POST /scheduler/api/chat/clear-history` - Clear chat history
- `GET /api/logs` - Get application logs
- `POST /api/logs/clear` - Clear logs

## Production

- Set `SESSION_COOKIE_SECURE=True` for HTTPS
- Disable debug mode
- Use environment variables for all secrets
- Configure MongoDB replica set for production workloads

## License

MIT
