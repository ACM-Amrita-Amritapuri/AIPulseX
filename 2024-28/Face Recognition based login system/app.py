import os

from flask import Flask,jsonify,render_template
from flask_jwt_extended import JWTManager  # type: ignore
from auth import auth_bp

app=Flask(__name__)
app.config['SECRET_KEY']=os.getenv('SECRET_KEY','dev-secret-key')
app.config.setdefault('APP_NAME', 'Nebula Lock')
app.config.setdefault('APP_YEAR', '2025')
app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY',app.config['SECRET_KEY'])

# jwt = JWTManager()
jwt=JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route('/')
def home():
    return render_template('auth_ui.html')

@app.route('/health')
def health_check():
    return jsonify({"message":"Server running well"})

if __name__=="__main__":
    app.run(debug=True)

