from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    # Process registration
    data = request.get_json()
    
    # Validate input
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    # Create new user
    hashed_password = generate_password_hash(data['password'])
    api_key = str(uuid.uuid4())  # Generate a unique API key
    
    new_user = User(
        email=data['email'], 
        password=hashed_password, 
        api_key=api_key
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully', 
            'api_key': api_key
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Similar modifications for other auth routes (update, delete)

@bp.route('/update', methods=['PUT'])
def update_api_key():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    new_api_key = user.generate_api_key()
    db.session.commit()
    
    return jsonify({'api_key': new_api_key}), 200

@bp.route('/delete', methods=['DELETE'])
def delete_api_key():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200