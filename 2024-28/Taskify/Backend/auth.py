import warnings
warnings.filterwarnings('ignore')

from flask import Blueprint,request,flash,render_template,redirect,url_for,session,jsonify
from flask_jwt_extended import create_access_token #type: ignore
from werkzeug.security import generate_password_hash,check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os 
import logging
from .utils import validate_password,validate_username
from functools import wraps

# Get application logger
app_logger = logging.getLogger('app')



load_dotenv()

# setting up mongo client
client=MongoClient(os.getenv("MONGODB_URI"))
db=client[os.getenv("DATABASE_NAME","Schedule_gen")]
user_col=db[os.getenv("COLLECTION_NAME","Users")]

# Setting up the blueprint
bp = Blueprint("auth", __name__)

# Creating the register and login routes
# Register Route
 

@bp.route("/register",methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_pass = request.form.get('confirm_password')

    

        # Checking the name 
        if not name:
            flash("Name is required")
            return render_template("register.html")
        
        
        # Validating the username 
        valid_name, user_issue = validate_username(username = username )
        if not valid_name:
            flash(user_issue, "warning")
            return render_template("register.html")

        
        # Step 1: Validate the entered password using a custom validation function
        # This checks for things like minimum length, special characters, uppercase letters, etc.
        valid_pass, pass_issue = validate_password(password)
        if not valid_pass:
            # If password doesn't meet requirements, show warning
            flash(pass_issue, "warning")
            return render_template("register.html")
        # Step 2: Verify that the entered password and confirm password fields match
        # This ensures the user didn’t mistype their password
        if password != confirm_pass:
            flash("Passwords do not match, try again", "warning")
            return render_template("register.html")
        
        # Step 3: Check if the username already exists in the database
        # This prevents duplicate accounts with the same username
        existing_user = user_col.find_one({"username": username})

        if existing_user:
            # Warn user to choose a different username
            flash("Username already exists. Please choose a different username.", "warning")
            return render_template("register.html")
        # Hashing the password
        try:
            hashed_pass=generate_password_hash(password=password) #type: ignore
        
            user_data={"username":username,
                   "password":hashed_pass,
                   'last_login': None,
                   'is_active': True
                   }
        
            res=user_col.insert_one(user_data)
        
            if res.inserted_id:
                app_logger.info(f'New user registered: {username}')
                flash("Registration Successful. You can login now!", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("Registration failed")
                return render_template('register.html')
        except Exception as e:
            app_logger.error(f'Registration error for user {username}: {str(e)}')
            flash("Error occurred during registration, try again")
            return render_template('register.html')
        
    return render_template('register.html') 


@bp.route("/login", methods=["POST"])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=user_col.find_one({"username":username})
        
        if not user:
            flash("User does not exist , try again")
            return render_template("login.html")
        
        if not username:
            flash("Username is Required")
            return render_template("login.html")
            
        if not password:
            flash("Password is required")
            return render_template("login.html")
        
        if not check_password_hash(user['password'],password=password):
            flash("Invalid Password , try again")
            return render_template("login.html")
            
        try:
            user_col.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': str(datetime.now())}}
            )
            
            # Creating session
            session['user_id']=str(user['_id'])
            session['username']=username
            session['logged_in']=True  # THIS IS THE MISSING LINE!
            
            # Creating access token
            token=create_access_token(identity=username)
            session['access_token']=token
            
            app_logger.info(f'User logged in: {username}')
            
            # Redirect to dashboard
            flash(f"Welcome back {username}!", "success")
            return redirect(url_for("dashboard"))
            
        
        except Exception as e:
            app_logger.error(f'Login error for user {username}: {str(e)}')
            flash("Error while logging in, try again",'error')
            
    return render_template("login.html")



# Creating route for changing password
@bp.route('/change-password',methods=['GET','POST'])
def change_password():
    if request.method=='POST':
        if 'user_id' not in session:
            flash("Login to access this page","error")
            redirect(url_for('auth.login'))
        
        user_id=session.get('user_id')
        try:
            password=request.form['password']
            new_password=request.form['new_password']
            confirm_new=request.form['confirm_new_password']
            user=user_col.find_one({'_id':user_id})
            
            if not user:
                flash("User not found","error")
                redirect(url_for('auth.login'))
                
# Verify the user's current password before proceeding with change
# The function 'check_password_hash' compares the stored hashed password 

            # safer access using .get()
            if not check_password_hash(user.get('password'), password):   #type: ignore
               flash("Invalid password. Please try again.", "warning")
            return render_template("change_password.html")
                        
            # Validating new password
            valid_pass,pass_issue=validate_password(password=new_password)
            if not valid_pass:
                flash(pass_issue)
                return render_template("change_password.html")
            
            if new_password!=confirm_new:
                flash("The passwords do not match")
                return render_template("change_password.html")
            
            # updating password
            hashed_pass=generate_password_hash(password=new_password)
            user_col.update_one(
                {'_id': user['_id']}, #type: ignore
                {'$set': {'password': hashed_pass, 'last_login': datetime.utcnow()}}
            )
            
            flash("Password updated successfully", "success")
            return redirect(url_for('dashboard'))
            

        except Exception as e:
            print(f"Error while changing the password:{e}")
            return render_template("change_password.html")


        
    
    return render_template("change_password.html")


# Creating logout route
@bp.route('/logout')
def logout():
    if "username" in session:
        username = session.get('username', 'Unknown')
        session.clear()
        
        # 🧹 Attempt to clear application logs during user logout
        try:
            # Import the app logging module dynamically (useful if not globally accessible)
            from app import app_logs
            # Clear all stored logs for the current session/user
            app_logs.clear_logs()
            # Log the successful log-clear event for tracking and debugging
            app_logger.info(f'Logs cleared for user: {username} on logout')
        except Exception as e: 
            # Log the error details for troubleshooting
            app_logger.error(f'Error clearing logs on logout: {str(e)}')
        

# -------------------------------------------------------------

# -------------------------------------------------------------

        flash("Successfully logged out","success")
    else:
        flash("You have to login first",'error')
        
    return redirect(url_for('auth.login'))




def login_check(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get("logged_in"):
            return f(*args, **kwargs)
        else:
            # Check if it's an AJAX request (for JSON responses)
            if (
                request.is_json
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.path.startswith("/Upload")
            ):
                return jsonify({"error": "Not authenticated"}), 401
            return redirect("/")
        
    return decorated_func
