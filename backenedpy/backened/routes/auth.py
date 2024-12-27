from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User

auth_bp = Blueprint('auth', __name__)

def init_auth_routes(mongo):

    @auth_bp.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not password or not name:
            return jsonify({'error': 'email and password are required'}), 400

        # Check if the username already exists
        existing_user = User.find_by_username(mongo, email)
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 409  # HTTP 409 Conflict

        # Hash the password
        hashed_password = generate_password_hash(password)
        new_user = User(email=email,name=name, password=hashed_password)

        # Save the new user to MongoDB
        try:
            new_user.save_to_db(mongo)
            return jsonify({'message': 'User created successfully'}), 201
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'User creation failed', 'details': str(e)}), 500

    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user_data = User.find_by_username(mongo, email)

        if user_data and check_password_hash(user_data['password'], password):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    return auth_bp
