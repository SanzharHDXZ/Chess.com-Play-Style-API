from flask import Blueprint, make_response, request, jsonify
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST', 'OPTIONS'])
def register_api_key():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(
        email=data['email'],
    )
    user.set_password(data['password'])
    user.generate_api_key()
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'api_key': user.api_key}), 201

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