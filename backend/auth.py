from flask import Blueprint, request, jsonify, make_response
from functools import wraps
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

# Initialize Blueprint
auth = Blueprint('auth', __name__)

# Secret key for JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

def get_db_connection():
    conn = sqlite3.connect(os.path.join('..', 'students.db'))
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            conn = get_db_connection()
            current_user = conn.execute('SELECT * FROM users WHERE id = ?', 
                                     (data['user_id'],)).fetchone()
            conn.close()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')  # 'student' or 'lecturer'
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400
    
    conn = get_db_connection()
    
    # Check if user exists
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user:
        conn.close()
        return jsonify({'message': 'User already exists!'}), 400
    
    # Create new user
    hashed_password = generate_password_hash(password, method='sha256')
    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, role))
    conn.commit()
    user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    
    return jsonify({'message': 'User created successfully!', 'user_id': user_id}), 201

@auth.route('/api/login', methods=['POST'])
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, 
                           {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (auth.username,)).fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], auth.password):
        return make_response('Could not verify', 401, 
                           {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY)
    
    return jsonify({'token': token, 'role': user['role']})
