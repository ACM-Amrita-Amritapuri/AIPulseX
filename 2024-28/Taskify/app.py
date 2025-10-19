import warnings
import os
import sys
import logging

# Suppress ALL warnings - must be first
warnings.filterwarnings('ignore')
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress specific warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Suppress absl logging (Google's logging library)
try:
    import absl.logging
    absl.logging.set_verbosity('error')
    absl.logging.set_stderrthreshold('error')
except:
    pass

# Redirect stderr to suppress C++ level errors temporarily during imports
class SuppressOutput:
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, *args):
        sys.stderr.close()
        sys.stderr = self._original_stderr

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_jwt_extended import JWTManager
from flask_compress import Compress

# Import with suppression
with SuppressOutput():
    from Backend.auth import auth_bp
    from Backend.Schedule_gen import doc_bp as document_bp
    from Backend.Schedule_gen import schedule_bp as scheduler_bp
    from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='Frontend/Templates', static_folder='Frontend/scripts')
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

# Enable compression for faster response times
Compress(app)

# Configure custom logging
from collections import deque
from datetime import datetime
import threading

# In-memory log storage (thread-safe)
class LogStorage:
    def __init__(self, max_size=1000):
        self.logs = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add_log(self, level, message, timestamp=None):
        with self.lock:
            self.logs.append({
                'timestamp': timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': level,
                'message': message
            })
    
    def get_logs(self, limit=None):
        with self.lock:
            if limit:
                return list(self.logs)[-limit:]
            return list(self.logs)
    
    def clear_logs(self):
        with self.lock:
            self.logs.clear()

# Global log storage
app_logs = LogStorage()

# Custom logging handler to capture application logs
class MemoryLogHandler(logging.Handler):
    def emit(self, record):
        try:
            # Skip HTTP request logs (they'll show in terminal)
            if 'GET' in record.getMessage() or 'POST' in record.getMessage() or 'PUT' in record.getMessage() or 'DELETE' in record.getMessage():
                return
            
            log_entry = self.format(record)
            app_logs.add_log(
                level=record.levelname,
                message=log_entry,
                timestamp=datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            )
        except Exception:
            self.handleError(record)

# Configure application logger
app_logger = logging.getLogger('app')
app_logger.setLevel(logging.INFO)
memory_handler = MemoryLogHandler()
memory_handler.setFormatter(logging.Formatter('%(name)s - %(message)s'))
app_logger.addHandler(memory_handler)

# Configure Werkzeug logging to show HTTP requests in terminal only
werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.INFO)
# Remove all handlers and add only console handler
werkzeug_log.handlers = []
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
werkzeug_log.addHandler(console_handler)
werkzeug_log.propagate = False

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'application/json', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching in development

# Initialize JWT Manager
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(document_bp)
app.register_blueprint(scheduler_bp)

@app.route('/')
def index():
    """Renders the landing page."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        flash("You need to be logged in to see this page.", "warning")
        return redirect(url_for('auth.login'))

@app.route('/scheduler')
def scheduler():
    if 'username' in session:
        return render_template('scheduler.html')
    else:
        flash("You need to be logged in to see this page.", "warning")
        return redirect(url_for('auth.login'))

@app.route('/documents')
def documents():
    if 'username' in session:
        return render_template('documents.html')
    else:
        flash("You need to be logged in to see this page.", "warning")
        return redirect(url_for('auth.login'))

@app.route('/logs')
def logs():
    if 'username' in session:
        # TODO: Add admin check
        return render_template('logs.html')
    else:
        flash("You need to be logged in to see this page.", "warning")
        return redirect(url_for('auth.login'))

@app.route('/api/logs')
def get_logs():
    """API endpoint to retrieve application logs"""
    if 'username' not in session:
        return {'error': 'Unauthorized'}, 401
    
    limit = request.args.get('limit', type=int, default=100)
    logs = app_logs.get_logs(limit=limit)
    return {'logs': logs}, 200

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """API endpoint to clear application logs"""
    if 'username' not in session:
        return {'error': 'Unauthorized'}, 401
    
    app_logs.clear_logs()
    app_logger.info('Logs cleared by user: ' + session.get('username', 'unknown'))
    return {'message': 'Logs cleared successfully'}, 200

@app.route('/activity-history')
def activity_history():
    if 'username' in session:
        return render_template('activity_history.html')
    else:
        flash("You need to be logged in to see this page.", "warning")
        return redirect(url_for('auth.login'))

# Redirect old /chat route to dashboard
@app.route('/chat')
def redirect_chat():
    flash("Chat is now integrated into the dashboard!", "info")
    return redirect(url_for('dashboard'))

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    # If someone tries to access /chat, redirect to dashboard
    if request.path == '/chat':
        flash("Chat is now on the dashboard!", "info")
        return redirect(url_for('dashboard'))
    # Check if 404 template exists
    template_path = 'Frontend/Templates/404.html'
    if os.path.exists(template_path):
        return render_template('404.html'), 404
    else:
        return "Page not found", 404

# Add cache control headers to prevent stale JavaScript
@app.after_request
def add_header(response):
    # Prevent caching of HTML and JS files for dynamic content
    if request.path.endswith('.html') or request.path.endswith('.js') or '/dashboard' in request.path:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    # Cache static assets for better performance
    elif request.path.startswith('/static/') or request.path.endswith(('.css', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
    return response

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Flask Server Starting...")
    print("="*60)
    print(f"🏠 Home: http://127.0.0.1:5000/")
    print("="*60 + "\n")
    
    # Log server startup
    app_logger.info('Flask application started')
    app_logger.info('Server running on http://127.0.0.1:5000/')
    
    # Disable reloader to prevent Windows WinError 10038
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)

