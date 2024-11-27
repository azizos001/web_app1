from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client.shopfront
users = db.users

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already exists'}), 400
        
    user = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'password': generate_password_hash(data['password']),
        'orders': []
    }
    users.insert_one(user)
    
    # Remove password from response
    del user['password']
    return jsonify(user), 201

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users.find_one({'id': user_id}, {'_id': False, 'password': False})
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users.find_one({'email': data['email']})
    
    if user and check_password_hash(user['password'], data['password']):
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    update_data = {}
    
    if 'name' in data:
        update_data['name'] = data['name']
    if 'email' in data:
        update_data['email'] = data['email']
    
    if update_data:
        result = users.update_one(
            {'id': user_id},
            {'$set': update_data}
        )
        if result.modified_count:
            user = users.find_one({'id': user_id}, {'_id': False, 'password': False})
            return jsonify(user)
    
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)