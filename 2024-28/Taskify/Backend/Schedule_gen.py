import warnings
warnings.filterwarnings('ignore')

from flask import Blueprint, render_template, flash, request, session, jsonify
from werkzeug.utils import secure_filename
from .auth import login_check
from .utils import process_doc, get_user_documents, get_context, process_schedule
import tempfile
import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime, timezone
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize logger
app_logger = logging.getLogger('app')
load_dotenv()

# Blueprints
doc_bp = Blueprint("document", __name__)
schedule_bp = Blueprint("scheduler", __name__, url_prefix='/scheduler')

# Model initialization
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)

# In-memory storage (temporary)
schedules = []
chats = {}

# ====================================================================
# 📁 DOCUMENT UPLOAD & MANAGEMENT
# ====================================================================

@doc_bp.route("/my-documents")
@login_check
def my_documents():
    """Display all documents uploaded by the current user."""
    username = session.get('username', '')
    documents = get_user_documents(username)
    return render_template('my_documents.html', documents=documents, username=username)


@doc_bp.route("/upload", methods=['POST'])
@login_check
def upload_docs():
    """Handle document uploads (PDF or DOCX)."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)

    if not filename:
        flash("Couldn't upload the file", "error")
        return jsonify({"error": "Invalid file name"}), 400

    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in ['pdf', 'docx']:
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        username = session.get('username', 'unknown')
        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = os.path.join(tmp_dir, filename)
            file.save(save_path)
            result, msg = process_doc(save_path, ext, username)

        if not result:
            app_logger.warning(f'Document processing failed for {username}: {msg}')
            raise Exception(msg)

        app_logger.info(f'Document uploaded successfully by {username}: {filename}')
        flash("Successfully processed the document!", "success")
        return jsonify({"message": "Document processed"}), 201

    except Exception as e:
        app_logger.error(f'Error uploading document for {username}: {str(e)}')
        return jsonify({"error": "Upload failed"}), 500


# ====================================================================
# 💬 CHAT SYSTEM
# ====================================================================

@schedule_bp.route("/api/chat/save-message", methods=['POST'])
@login_check
def save_message():
    """Save a user message without AI response."""
    data = request.get_json() or {}
    message = (data.get('message', '') or '').strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    session_id = session.get("username", "anon")
    chats.setdefault(session_id, [])

    chats[session_id].append({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'user_message': message[:500],
        'bot_response': None
    })

    # Keep latest 50 messages
    chats[session_id] = chats[session_id][-50:]
    return jsonify({"status": "saved"}), 200


@schedule_bp.route("/api/chat/message", methods=['POST'])
@login_check
def chat():
    """Handle user chat messages with AI responses."""
    data = request.get_json() or {}
    message = (data.get('message', '') or '').strip()
    intent = data.get('intent', 'chat')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Context summary of latest schedules
        context_summary = ""
        if schedules:
            recent = schedules[-5:]
            lines = [f"- {s.get('title', 'Untitled')} ({len(s.get('tasks', []))} tasks)" for s in recent]
            context_summary = "\nRecent schedules:\n" + "\n".join(lines)

        # Dynamic prompt
        if intent == 'schedule_prep':
            prompt = f"""You are a friendly AI scheduling assistant.
The user said: "{message}"
Acknowledge briefly (1-2 sentences) and mention you'll use this info when creating their schedule."""
        else:
            prompt = f"""You are a helpful AI schedule assistant.
User asked: "{message}"
{context_summary}

Respond concisely. If it's about planning, remind them they can click 'Generate Schedule'."""

        llm_response = llm.invoke(prompt)
        reply = str(getattr(llm_response, 'content', llm_response)).strip()

        response = {"message": reply}

    except Exception as e:
        app_logger.error(f"Chat error: {e}")
        response = {"message": "I'm your AI scheduling assistant! I can help you plan, organize, and stay productive."}

    # Save chat
    session_id = session.get("username", "anon")
    chats.setdefault(session_id, [])
    chats[session_id].append({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'user_message': message[:500],
        'bot_response': response
    })
    chats[session_id] = chats[session_id][-50:]

    return jsonify(response)


@schedule_bp.route("/api/chat/history", methods=['GET'])
@login_check
def chat_history():
    """Return recent chat history for the logged-in user."""
    session_id = session.get("username", "anon")
    return jsonify(chats.get(session_id, []))


@schedule_bp.route("/api/chat/clear-history", methods=['POST'])
@login_check
def clear_chat_history():
    """Clear chat history for the user."""
    session_id = session.get("username", "anon")
    chats[session_id] = []
    return jsonify({"message": "Chat history cleared"})


# ====================================================================
# 🗓️ SCHEDULE GENERATION & MANAGEMENT
# ====================================================================

@schedule_bp.route("/api/generate", methods=['POST'])
@login_check
def generate_schedule():
    """Generate a new AI schedule from user input."""
    payload = request.get_json() or {}
    user_input = (payload.get('input', '') or '').strip()
    title = (payload.get('title', 'AI Generated Schedule') or '').strip()
    description = (payload.get('description', '') or '').strip()

    if not user_input:
        return jsonify({"error": "Input is required"}), 400

    try:
        username = session.get('username', 'unknown')
        context, _ = get_context(user_input)
        schedule = process_schedule(user_input, context)

        schedule_obj = {
            **schedule,
            "id": f"sch-{len(schedules) + 1}",
            "title": title or schedule.get("title", "AI Generated Schedule"),
            "description": description or schedule.get("description", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": username,
            "status": "active"
        }

        schedules.append(schedule_obj)
        app_logger.info(f"Schedule generated for {username}: {title}")
        return jsonify(schedule_obj), 201

    except Exception as e:
        app_logger.error(f"Error generating schedule: {str(e)}")
        return jsonify({"error": "Failed to generate schedule"}), 500


@schedule_bp.route("/api/schedules", methods=['GET'])
@login_check
def list_schedules():
    """List all schedules."""
    return jsonify(schedules)


@schedule_bp.route("/api/schedules/<sid>", methods=['GET', 'DELETE'])
@login_check
def handle_schedule(sid):
    """Get or delete a schedule by ID."""
    global schedules
    if request.method == 'GET':
        for s in schedules:
            if s.get('id') == sid:
                return jsonify(s)
        return jsonify({"error": "Not found"}), 404

    # DELETE
    before = len(schedules)
    schedules = [s for s in schedules if s.get('id') != sid]
    if len(schedules) == before:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted successfully"})


@schedule_bp.route("/api/generate-from-chat", methods=['POST'])
@login_check
def generate_from_chat():
    """Generate a schedule using the latest chat message."""
    session_id = session.get("username", "anon")
    history = chats.get(session_id, [])
    latest_message = next((m.get('user_message') for m in reversed(history) if m.get('user_message')), None)

    if not latest_message:
        return jsonify({"error": "No recent chat message found. Try chatting first!"}), 400

    payload = request.get_json(silent=True) or {}
    title = (payload.get('title') or 'AI Generated Schedule').strip()
    description = (payload.get('description') or '').strip()

    try:
        app_logger.debug(f"Generating from chat for {session_id}: {latest_message}")
        context, _ = get_context(latest_message)
        schedule = process_schedule(latest_message, context)

        schedule_obj = {
            **schedule,
            "id": f"sch-{len(schedules) + 1}",
            "title": title or schedule.get("title", "AI Generated Schedule"),
            "description": description or schedule.get("description", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": session_id,
            "status": "active"
        }

        schedules.append(schedule_obj)
        return jsonify(schedule_obj), 201

    except Exception as e:
        app_logger.error(f"Error generating schedule from chat: {e}")
        return jsonify({"error": "Failed to generate schedule from chat"}), 500
