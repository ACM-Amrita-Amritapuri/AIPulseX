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
@auth_bp.route("/register",methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    raw_password = data.get("password")
    raw_confirm = data.get("confirm_password")
    password = raw_password if isinstance(raw_password, str) else ""
    confirm_pass = raw_confirm if isinstance(raw_confirm, str) else ""
    face = data.get("face_image")

    issues = []
    if not username:
        issues.append("Username is required.")
    if not password:
        issues.append("Password is required.")
    if password != confirm_pass:
        issues.append("Passwords do not match.")
    if not face:
        issues.append("Face snapshot missing. Enable the camera and capture a frame.")

    if issues:
        return jsonify({'status': 'error', 'message': issues[0], 'messages': issues}), 400

    users = load_users() or {}

    if username in users:
        return jsonify({'status': 'error', 'message': 'User already registered.'}), 409

    img = decode_base64_image(face)
    if img is None:
        return jsonify({'status': 'error', 'message': 'Unable to decode face snapshot. Please recapture and retry.'}), 400

    embeddings = get_embeddings(img)
    if embeddings is None:
        return jsonify({'status': 'error', 'message': 'Unable to process facial embedding. Adjust lighting and try again.'}), 400

    # embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR")
    embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or DEFAULT_EMBEDDING_DIR
    if not embeddings_dir:
        return jsonify({'status': 'error', 'message': 'Embeddings directory is not configured on the server.'}), 500

    os.makedirs(embeddings_dir, exist_ok=True)
    embedding_path = os.path.join(embeddings_dir, f"{username}.npy")

    np.save(embedding_path, embeddings)

    hashed_pass = generate_password_hash(password=password)

    users[username] = {'password': hashed_pass}
    save_users(users)

    return jsonify({'status': 'success', 'message': 'Face embedding generated and user registered successfully.'})

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

@auth_bp.route("/login_face", methods=['POST'])
def login_face():
    """
    Authenticate user via facial recognition.
    Performs up to 3 retry attempts before fallback to credential login.
    """
    data = request.get_json(silent=True) or {}

    # Fixed: typo and inconsistent key fallback
    username = (data.get("username") or "").strip()
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
            return jsonify({
                'status': 'retry',
                'message': f'Unable to read face. {3 - attempt} attempt(s) left.',
                'attempt': attempt + 1
            }), 401
        return jsonify({'status': 'error', 'message': 'Unable to read facial data. Use credential login instead.'}), 401

    embedding = get_embeddings(image=img)
    if embedding is None:
        if attempt < 3:
            return jsonify({
                'status': 'retry',
                'message': f'Face not recognized. {3 - attempt} attempt(s) left.',
                'attempt': attempt + 1
            }), 401
        return jsonify({'status': 'error', 'message': 'Face authentication failed. Use credential login.'}), 401

    # Fixed: ensure fallback path is always set correctly
    embeddings_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or DEFAULT_EMBEDDING_DIR
    if not embeddings_dir:
        return jsonify({'status': 'error', 'message': 'Embeddings directory not configured on the server.'}), 500

    embedding_path = os.path.join(embeddings_dir, f"{username}.npy")

    # Added: existence and file integrity checks
    if not os.path.exists(embedding_path):
        return jsonify({'status': 'error', 'message': 'No stored embedding found. Please re-register.'}), 404

    try:
        stored_emb = np.load(embedding_path)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Corrupted embedding file: {e}'}), 500

    # Safe embedding comparison
    if not compare_embeddings(emb1=embedding, emb2=stored_emb):
        if attempt < 3:
            return jsonify({
                'status': 'retry',
                'message': f'Face not recognized. {3 - attempt} attempt(s) left.',
                'attempt': attempt + 1
            }), 401
        return jsonify({'status': 'error', 'message': 'Face authentication failed. Use credential login.'}), 401

    # Token creation and session handling
    token = create_access_token(identity=username)
    session['username'] = username
    session['access token'] = token

    return jsonify({
        'status': 'success',
        'message': f'Authentication successful for user {username}.',
        'token_preview': f"{token[:18]}…{token[-6:]}" if len(token) > 32 else token
    })

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



