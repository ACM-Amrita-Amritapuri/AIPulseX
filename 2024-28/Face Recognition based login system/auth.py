from flask import Blueprint,request,jsonify,session,render_template
from flask_jwt_extended import create_access_token #type: ignore
from werkzeug.security import generate_password_hash,check_password_hash
from dotenv import load_dotenv
from utils import get_embeddings,compare_embeddings,decode_base64_image,load_users,save_users,embedding_dir as DEFAULT_EMBEDDING_DIR
import numpy as np
import os


load_dotenv()


auth_bp=Blueprint("Auth",__name__)

"""Creating the register route"""
@auth_bp.route("/dashboard", methods=['GET'])
def dashboard():
    username = session.get('username')
    # 🔧 Fixed session key name (no space)
    token_value = session.get('access_token')

    token_preview = None
    if isinstance(token_value, str) and token_value:
        token_preview = f"{token_value[:18]}…{token_value[-6:]}" if len(token_value) > 32 else token_value

    face_ready = False
    if username:
        embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or DEFAULT_EMBEDDING_DIR
        if embeddings_dir:
            embedding_path = os.path.join(embeddings_dir, f"{username}.npy")
            face_ready = os.path.exists(embedding_path)

    return render_template('dashboard.html', username=username, face_ready=face_ready, token_preview=token_preview)


@auth_bp.route("/login_face", methods=['POST'])
def login_face():
    data = request.get_json(silent=True) or {}

    # ✅ kept the fallback for 'usernmae' but corrected logic order
    username = (data.get("username") or data.get("usernmae") or "").strip()
    face = data.get("face_image")
    attempt_value = data.get('attempt', 1)

    try:
        attempt = int(attempt_value)
    except (TypeError, ValueError):
        attempt = 1

    issues = []
    if not username:
        issues.append("Username is required.")
    if not face:
        issues.append("Face snapshot missing.")

    if issues:
        return jsonify({'status': 'error', 'message': issues[0], 'messages': issues}), 400

    users = load_users() or {}
    if username not in users:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404

    img = decode_base64_image(image=face)
    if img is None:
        if attempt < 3:
            return jsonify({'status': 'retry', 'message': f'Unable to read face. {3 - attempt} attempt(s) left.', 'attempt': attempt + 1}), 401
        return jsonify({'status': 'error', 'message': 'Unable to read facial data. Use credential login instead.'}), 401

    embedding = get_embeddings(image=img)
    if embedding is None:
        if attempt < 3:
            return jsonify({'status': 'retry', 'message': f'Face not recognized. {3 - attempt} attempt(s) left.', 'attempt': attempt + 1}), 401
        return jsonify({'status': 'error', 'message': 'Face authentication failed. Use credential login.'}), 401

    embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or DEFAULT_EMBEDDING_DIR
    if not embeddings_dir:
        return jsonify({'status': 'error', 'message': 'Embeddings directory is not configured on the server.'}), 500

    os.makedirs(embeddings_dir, exist_ok=True)
    embedding_path = os.path.join(embeddings_dir, f"{username}.npy")
    if not os.path.exists(embedding_path):
        return jsonify({'status': 'error', 'message': 'No stored embedding found. Please re-register.'}), 404

    stored_emb = np.load(embedding_path)

    if not compare_embeddings(emb1=embedding, emb2=stored_emb):
        if attempt < 3:
            return jsonify({'status': 'retry', 'message': f'Face not recognized. {3 - attempt} attempt(s) left.', 'attempt': attempt + 1}), 401
        return jsonify({'status': 'error', 'message': 'Face authentication failed. Use credential login.'}), 401

    token = create_access_token(identity=username)
    session['username'] = username
    # 🔧 Fixed here too (no space)
    session['access_token'] = token
    return jsonify({'status': 'success', 'message': 'Authentication successful.'})


@auth_bp.route("/login_cred", methods=['POST'])
def login_cred():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password_value = data.get("password")
    password = password_value if isinstance(password_value, str) else ""

    issues = []
    if not username:
        issues.append("Username is required.")
    if not password:
        issues.append("Password is required.")

    if issues:
        return jsonify({'status': 'error', 'message': issues[0], 'messages': issues}), 400

    users = load_users() or {}

    if username not in users:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404

    hashed_pass = users[username].get('password')
    if not hashed_pass or not check_password_hash(hashed_pass, password=password):
        return jsonify({'status': 'error', 'message': 'Incorrect username or password.'}), 401

    token = create_access_token(identity=username)
    session['username'] = username
    # 🔧 Consistent fix
    session['access_token'] = token

    return jsonify({'status': 'success', 'message': 'Credential login successful.'})

@auth_bp.route("/login", methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route("/dashboard", methods=['GET'])
def dashboard():
    username = session.get('username')
    token_value = session.get('access token')

    token_preview = None
    if isinstance(token_value, str) and token_value:
        token_preview = f"{token_value[:18]}…{token_value[-6:]}" if len(token_value) > 32 else token_value

    face_ready = False
    if username:
        embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or DEFAULT_EMBEDDING_DIR
        if embeddings_dir:
            embedding_path = os.path.join(embeddings_dir, f"{username}.npy")
            face_ready = os.path.exists(embedding_path)

    return render_template('dashboard.html', username=username, face_ready=face_ready, token_preview=token_preview)

@auth_bp.route("/login_face",methods=['POST'])
def login_face():
    """
    Authenticate user via facial recognition.
    Performs up to 3 retry attempts before fallback to credential login.
    """
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or data.get("usernmae") or "").strip()
    face = data.get("face_image")
    attempt_value = data.get('attempt', 1)

    try:
        attempt = int(attempt_value)
    except (TypeError, ValueError):
        attempt = 1

    issues = []
    if not username:
        issues.append("Username is required.")
    if not face:
        issues.append("Face snapshot missing.")

    if issues:
        return jsonify({'status': 'error', 'message': issues[0], 'messages': issues}), 400

    users = load_users() or {}
    if username not in users:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404

    img = decode_base64_image(image=face)
    if img is None:
        if attempt < 3:
            return jsonify({'status': 'retry', 'message': f'Unable to read face. {3 - attempt} attempt(s) left.', 'attempt': attempt + 1}), 401
        return jsonify({'status': 'error', 'message': 'Unable to read facial data. Use credential login instead.'}), 401

    embedding = get_embeddings(image=img)
    if embedding is None:
        if attempt < 3:
            return jsonify({'status': 'retry', 'message': f'Face not recognized. {3 - attempt} attempt(s) left.', 'attempt': attempt + 1}), 401
        return jsonify({'status': 'error', 'message': 'Face authentication failed. Use credential login.'}), 401

    # embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR")
    embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or DEFAULT_EMBEDDING_DIR
    if not embeddings_dir:
        return jsonify({'status': 'error', 'message': 'Embeddings directory is not configured on the server.'}), 500

    embedding_path = os.path.join(embeddings_dir, f"{username}.npy")

    # Added: existence and file integrity checks
    if not os.path.exists(embedding_path):
        return jsonify({'status': 'error', 'message': 'No stored embedding found. Please re-register.'}), 404

    stored_emb = np.load(embedding_path)

    # Safe embedding comparison
    if not compare_embeddings(emb1=embedding, emb2=stored_emb):
        if attempt < 3:
            return jsonify({'status': 'retry', 'message': f'Face not recognized. {3 - attempt} attempt(s) left.', 'attempt': attempt + 1}), 401
        return jsonify({'status': 'error', 'message': 'Face authentication failed. Use credential login.'}), 401

    # Token creation and session handling
    token = create_access_token(identity=username)
    session['username'] = username
    session['access token'] = token
    return jsonify({'status': 'success', 'message': 'Authentication successful.'})

@auth_bp.route("/login_cred",methods=['POST'])
def login_cred():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password_value = data.get("password")
    password = password_value if isinstance(password_value, str) else ""

    issues = []
    if not username:
        issues.append("Username is required.")
    if not password:
        issues.append("Password is required.")

    if issues:
        return jsonify({'status': 'error', 'message': issues[0], 'messages': issues}), 400

    users = load_users() or {}

    if username not in users:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404

    hashed_pass = users[username].get('password')
    if not hashed_pass or not check_password_hash(hashed_pass, password=password):
        return jsonify({'status': 'error', 'message': 'Incorrect username or password.'}), 401

    token = create_access_token(identity=username)
    session['username'] = username
    session['access token'] = token

    return jsonify({'status': 'success', 'message': 'Credential login successful.'})



