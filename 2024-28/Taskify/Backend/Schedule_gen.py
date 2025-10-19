import warnings
warnings.filterwarnings('ignore')

from flask import Blueprint,render_template,flash,request,session,jsonify
from werkzeug.utils import secure_filename
from .auth import login_check 
from .utils import process_doc, get_user_documents
import tempfile
import os
import json
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
from .utils import get_context,process_schedule

# Get application logger
app_logger = logging.getLogger('app')

load_dotenv()

doc_bp=Blueprint("document",__name__)
schedule_bp=Blueprint("scheduler",__name__,url_prefix='/scheduler')


llm=ChatGoogleGenerativeAI(model="gemini-2.5-pro",temperature=0.2) 

schedules=[]
chats={}


@doc_bp.route("/my-documents")
@login_check
def my_documents():
    """Display all documents uploaded by the current user."""
    username = session.get('username', '')
    documents = get_user_documents(username)
    return render_template('my_documents.html', documents=documents, username=username)


@doc_bp.route("/Upload",methods=['POST'])
@login_check
def upload_docs():
    
    if not request.files:
        flash("No files selected",'error')
        return jsonify({"error":"No file provided"}),400
    f_name=secure_filename(request.files['file'].filename) #type: ignore
    
    
    if not f_name:
        flash("Couldnt uplaod the file","file")
        return jsonify({"error":"Invalid file name"}),400
    
    if f_name.endswith(".pdf"):
        doc_type="pdf"
    elif f_name.endswith(".docx"):
        doc_type="docx"
    else:
        return jsonify({"error":"Unsupported file type"}),400
        
    try:
        username = session.get('username', 'unknown')
        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path=os.path.join(tmp_dir,f_name)
            request.files['file'].save(save_path)
            
            res,msg=process_doc(save_path, doc_type, username)
        
        if not res:
            app_logger.warning(f'Document processing failed for {username}: {msg}')
            flash("Couldn't process document","error")
            raise Exception(msg)
        
        app_logger.info(f'Document uploaded successfully by {username}: {f_name}')
        flash("Successfully processed the document!", "success")
        return jsonify({"message":"Document processed"}),201
        
    except Exception as e:
        app_logger.error(f'Error uploading document for {username}: {str(e)}')
        flash("Error while uploading document")
        return jsonify({"error":"Upload failed"}),500

@schedule_bp.route("/api/chat/save-message", methods=['POST'])
def save_message():
    """Save a user message to chat history without generating a response."""
    data = request.get_json() or {}
    message = (data.get('message', '') or '').strip()
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    # Save to session storage
    session_id = session.get("username", "anon")
    if session_id not in chats:
        chats[session_id] = []
    
    # Append message
    chats[session_id].append({
        'timestamp': datetime.now().isoformat(),
        'user_message': message[:500],
        'bot_response': None  # No response yet
    })
    
    if len(chats[session_id]) > 50:
        chats[session_id] = chats[session_id][-50:]
    
    return jsonify({"status": "saved"}), 200


@schedule_bp.route("//api/chat/message",methods=['POST'])
def chat():
    data=request.get_json() or {}
    message=(data.get('message','') or '').strip()
    intent = data.get('intent', 'chat')  # 'chat' or 'schedule_prep'
    
    if not message:
        return jsonify({"error":"Message is required"}),400

    try:
        # Get existing schedules for context
        schedule_context = ""
        if schedules:
            schedule_list = []
            for s in schedules[-5:]:  # Last 5 schedules
                tasks_summary = ", ".join([t.get('title', '') for t in s.get('tasks', [])[:3]])
                schedule_list.append(f"- {s.get('title', 'Untitled')}: {tasks_summary}")
            schedule_context = "\n\nYour recent schedules:\n" + "\n".join(schedule_list)
        
        # Create schedule-aware prompt based on intent
        if intent == 'schedule_prep':
            # User is preparing to generate a schedule, provide brief acknowledgment
            enhanced_message = f"""You are a helpful AI schedule assistant. The user has said: "{message}"

Provide a brief, encouraging acknowledgment (1-2 sentences) confirming you understand their request. Mention that you'll use this information when they generate their schedule."""
        else:
            # Regular chat interaction
            enhanced_message = f"""You are a helpful AI schedule assistant. The user has asked: "{message}"
{schedule_context}

Provide a helpful, concise response. If they're asking about scheduling, remind them they can click 'Generate Schedule' to create a personalized schedule."""
        
        # Use streaming for faster response (if supported)
        response=llm.invoke(enhanced_message).content or ""
        response_str=str(response).strip()
        
        # Simple response without suggestions
        llm_response = {
            "message": response_str
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        # Fallback to simple response if LLM fails
        llm_response = {
            "message": "I'm your AI schedule assistant! I can help you create schedules, manage tasks, and provide productivity tips. Just tell me what you want to do!"
        }
    
    # Optimize session storage
    session_id=session.get("username","anon") 
    if session_id not in chats:
        chats[session_id]=[]
    
    # Keep only last 50 messages to prevent memory bloat
    chats[session_id].append({
        'timestamp': datetime.now().isoformat(),
        'user_message': message[:500],  # Limit stored message length
        'bot_response': llm_response
    })
    
    if len(chats[session_id]) > 50:
        chats[session_id] = chats[session_id][-50:]
    
    return jsonify(llm_response)


@schedule_bp.route("/api/generate",methods=['POST'])
def generate_schedule():
    message=request.get_json() or {}
    user_input=(message.get('input','') or '').strip()
    title=message.get('title','AI Generated Schedule') or 'AI Generated Schedule'
    description=message.get('description','') or ''
    
    if not user_input:
        return jsonify({"error": "Input is required"}), 400
    
    try:
        username = session.get('username', 'unknown')
        context,_analysis=get_context(user_input)
        schedule=process_schedule(user_input,context)
        # enrich for frontend list
        schedule_obj={
            **schedule,
            "id": f"sch-{len(schedules)+1}",
            "title": title or schedule.get("title","AI Generated Schedule"),
            "description": description or schedule.get("description",""),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        schedules.append(schedule_obj)
        app_logger.info(f'Schedule generated for {username}: {title}')
        return jsonify(schedule_obj), 201
    
    except Exception as e:
        app_logger.error(f'Error generating schedule: {str(e)}')
        return jsonify({"error": "Failed to generate schedule"}), 500


@schedule_bp.route('/api/schedules',methods=['GET'])
def list_schedules():
    return jsonify(schedules)

@schedule_bp.route('/api/schedules/<sid>', methods=['GET'])
def get_schedule(sid):
    for s in schedules:
        if s.get('id') == sid:
            return jsonify(s)
    return jsonify({"error": "Not found"}), 404


@schedule_bp.route('/api/generate-from-chat', methods=['POST'])
def generate_from_chat():
    """Generate a schedule using the latest chat message from the current session."""
    session_id = session.get("username", "anon")
    history = chats.get(session_id, [])
    latest_message = None
    for m in reversed(history):
        text = (m.get('user_message', '') or '').strip()
        if text:
            latest_message = text
            break

    if not latest_message:
        return jsonify({"error": "No recent chat message found. Send a message in the dashboard chat first."}), 400

    payload = request.get_json(silent=True) or {}
    title = (payload.get('title') or '').strip() or 'AI Generated Schedule'
    description = (payload.get('description') or '').strip()

    try:
        print(f"\n=== SCHEDULE GENERATION DEBUG ===")
        print(f"User query: {latest_message}")
        context, _analysis = get_context(latest_message)
        print(f"Context retrieved (length): {len(context) if context else 0}")
        print(f"Context preview: {context[:200] if context else 'EMPTY CONTEXT'}...")
        schedule = process_schedule(latest_message, context)
        print(f"Schedule generated: {json.dumps(schedule, indent=2)}")
        print(f"=== END DEBUG ===")

        schedule_obj = {
            **schedule,
            "id": f"sch-{len(schedules)+1}",
            "title": title or schedule.get("title", "AI Generated Schedule"),
            "description": description or schedule.get("description", ""),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        schedules.append(schedule_obj)
        return jsonify(schedule_obj), 201
    except Exception as e:
        print(f"Error while generating schedule from chat {e}")
        return jsonify({"error": "Failed to generate schedule from chat"}), 500

@schedule_bp.route('/api/chat/history',methods=['GET'])
def chat_history():
    session_id=session.get("username","anon")
    return jsonify(chats.get(session_id,[]))

@schedule_bp.route('/api/chat/clear-history',methods=['POST'])
def clear_chat_history():
    session_id=session.get("username","anon")
    chats[session_id]=[]
    return jsonify({"message":"cleared"})

@schedule_bp.route('/api/chat/schedules',methods=['GET'])
def chat_schedules():
    return jsonify(schedules)

@schedule_bp.route('/api/schedules/<sid>',methods=['DELETE'])
def delete_schedule(sid):
    global schedules
    before=len(schedules)
    schedules=[s for s in schedules if s.get('id')!=sid]
    if len(schedules)==before:
        return jsonify({"error":"Not found"}),404
    return jsonify({"message":"deleted"})