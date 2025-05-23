from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file, session
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash, generate_password_hash
from flask_pymongo import PyMongo
import gridfs
from werkzeug.utils import secure_filename
from bson import ObjectId
from io import BytesIO
from collections import defaultdict
from datetime import datetime
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

bcrypt = Bcrypt(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Home page route
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        try:
            # Create Firebase user
            user = auth.create_user(email=email, password=password)
            
            # Set display name (optional)
            auth.update_user(user.uid, display_name=fullname)

            # Automatically assign admin role to specific emails
            if email in ["meenakshi16rp@gmail.com", "otheradmin@domain.com"]:
                auth.set_custom_user_claims(user.uid, {"role": "admin"})

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('signin'))
        
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Sign in user (Firebase does not check passwords on backend)
            user = auth.get_user_by_email(email)
            
            # Get the user's role from custom claims
            claims = user.custom_claims if user.custom_claims else {}
            role = claims.get("role", "user")  # Default to 'user' if no role exists
            
            # Store role in session for easy access
            session['user_role'] = role
            
            flash("Login successful. Redirecting...", "success")

            # Redirect based on role
            if role == "admin":
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('upload'))

        except Exception as e:
            flash(f"Login failed: {str(e)}", "danger")
            return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    try:
        auth.generate_password_reset_link(email)  # Firebase sends a reset link
        flash("Password reset instructions have been sent to your email.", "success")
    except firebase_admin.auth.UserNotFoundError:
        flash("Email not found, please try again.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for('signin'))

@app.route('/logout')
#@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route('/sessionLogin', methods=['POST'])
def session_login():
    data = request.get_json()
    id_token = data.get('idToken')

    try:
        decoded_token = auth.verify_id_token(id_token)
        role = decoded_token.get("role", "user")
        # Store role and email in session
        session['user_role'] = role
        session['email'] = decoded_token.get('email')

        return jsonify({"message": "Session set", "role": role}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get("user_role") != "admin":
        flash("Access Denied: Admins Only!", "danger")
        return redirect(url_for('home'))  # Redirect to user page
    return render_template('admin_dashboard.html')

# Get all users (Admin only)
@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = auth.list_users().iterate_all()
    
    user_list = []
    for user in users:
        # Ensure claims exist before accessing (the code will not crash of a user has no role assigned)
        claims = user.custom_claims if user.custom_claims else {}
        role = claims.get("role", "user")  # Default role is "user"
        user_list.append({
            "uid": user.uid,
            "email": user.email,
            "fullname": user.display_name if user.display_name else "N/A",
            "role": role
        })
    
    return jsonify(user_list)

# Assign role to user (Admin only)
@app.route('/assign_role/<uid>', methods=['POST'])
def assign_role(uid):
    role = request.json.get("role")
    if role not in ["admin", "user"]:
        return jsonify({"error": "Invalid role"}), 400
    auth.set_custom_user_claims(uid, {"role": role})
    return jsonify({"message": "Role updated successfully"})

# Delete user (Admin only)
@app.route('/delete_user/<uid>', methods=['DELETE'])
def delete_user(uid):
    try:
        auth.delete_user(uid)
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

from together import Together
import base64
import tempfile

client = Together(api_key="51df07beb081982c5b1a919b3f91662e2a5b322211ec358b79bc7135d914fede")  # Use your actual key

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        file.save(temp_file.name)
        with open(temp_file.name, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode()

    prompt = """The user will provide images mostly related to Indian monuments, Indian dances, Indian art, Indian historical figures.
    Analyze the image and give one word output for the thing in the image. If it's a monument then just tell the name of the monument and its location and nothing else.
    If the image depicts a dance then just give the name of the dance and nothing else. If the image depicts a potrait of a person then just give the name of the figure
    and nothing else. Keep the response as just the name of the thing depicted in the image and no extra text."""

    response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}
        ],
        max_tokens=50,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )

    description = response.choices[0].message.content.strip()
    return jsonify({"description": description})

 
@app.route('/get_user_uploads/<uid>', methods=['GET'])
def get_user_uploads(uid):
    try:
        # Assuming each file has a 'user_id' field when uploaded
        files = mongo.db['fs.files'].find({"user_id": uid})
        uploads = []
        for file in files:
            uploads.append({
                "file_id": str(file["_id"]),
                "filename": file["filename"],
                "content_type": file.get("contentType", "unknown"),
                "upload_date": file.get("uploadDate", ""),
            })
        return jsonify(uploads)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/file/preview/<file_id>', methods=['GET'])
def preview_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), mimetype=file.content_type)
    except Exception:
        return jsonify({"error": "File not found"}), 404

@app.route('/analytics/uploads_over_time', methods=['GET'])
def uploads_over_time():
    uploads = list(mongo.db['fs.files'].find({}, {"uploadDate": 1, "userId": 1}))

    # Group data
    upload_counts = defaultdict(lambda: defaultdict(int))
    for upload in uploads:
        user = upload.get("userId", "unknown")
        date = upload.get("uploadDate")
        if isinstance(date, datetime):
            date_str = date.date().isoformat()
        else:
            try:
                date_str = datetime.fromisoformat(str(date)).date().isoformat()
            except:
                continue
        upload_counts[user][date_str] += 1

    # Get sorted dates and format datasets
    all_dates = sorted(set(date for user_data in upload_counts.values() for date in user_data))
    datasets = []
    import random

    for user, date_data in upload_counts.items():
        data = [date_data.get(date, 0) for date in all_dates]
        color = f"rgb({random.randint(50,200)}, {random.randint(50,200)}, {random.randint(50,200)})"
        datasets.append({
            "label": user,
            "data": data,
            "borderColor": color,
            "backgroundColor": color,
            "fill": False
        })

    return jsonify({
        "labels": all_dates,
        "datasets": datasets
    })

def verify_firebase_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        id_token = request.headers.get("Authorization")
        if not id_token:
            return jsonify({"error": "Missing token"}), 401

        try:
            decoded_token = auth.verify_id_token(id_token)
            g.user = {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "role": decoded_token.get("role", "user")
            }
        except Exception as e:
            print("Token verification failed:", e)
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)
    return wrapper       
# Make sure CORS is imported if needed
from flask_cors import CORS
CORS(app, origins=["http://127.0.0.1:5500"])  # Enable CORS if you have cross-origin requests

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://divanshityagi21:5Ogy1brCYcuwXcJx@clustertest.pnkoi.mongodb.net/digitalarchiving"
mongo = PyMongo(app)

# GridFS instance
fs = gridfs.GridFS(mongo.db)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mov", "pdf"}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

# File Handling Routes
@app.route('/files/upload', methods=['POST','GET'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Extract metadata
        user_id = g.user['uid']  # From Firebase token verification
        upload_date = datetime.utcnow()
        content_type = file.content_type

        # Save to GridFS with metadata
        fs = gridfs.GridFS(mongo.db)

        file_id = fs.put(file, filename=filename, content_type=file.content_type, user_id=session.get("user_id"),metadata={
                'userId': user_id,
                'uploadDate': upload_date,
                'originalName': filename
            })
        return jsonify({"message": "File uploaded successfully", "file_id": str(file_id)}), 201
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/files/download/<file_id>', methods=['GET'])
def download_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), mimetype=file.content_type, as_attachment=True, download_name=file.filename)
    except Exception:
        return jsonify({"error": "File not found"}), 404

@app.route('/files/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        fs.delete(ObjectId(file_id))
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception:
        return jsonify({"error": "File not found"}), 404

@app.route('/files/list', methods=['GET'])
def list_files():
    files = mongo.db['fs.files'].find({}, {"_id": 1, "filename": 1})
    file_list = [{"file_id": str(file["_id"]), "filename": file["filename"]} for file in files]
    return jsonify(file_list), 200
    
@app.route('/files/post', methods=['POST'])
def upload_with_metadata():
    file = request.files['file']
    metadata = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "date": request.form.get("date"),
        "language": request.form.get("language"),
        "state": request.form.get("state"),
        "user": request.form.get("user"),
        "author": request.form.get("author"),
        "tags": request.form.get("tags")
    }
    file_id = fs.put(file, filename=file.filename, metadata=metadata)
    return jsonify({"file_id": str(file_id)}), 200
# Run the app
if __name__ == "__main__":
    app.run(debug=True)
