from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client.shopfront
orders = db.orders

@app.route('/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id')
    if user_id:
        order_list = list(orders.find({'userId': user_id}, {'_id': False}))
    else:
        order_list = list(orders.find({}, {'_id': False}))
    return jsonify(order_list)

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.find_one({'id': order_id}, {'_id': False})
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    order = {
        'id': str(uuid.uuid4()),
        'userId': data['userId'],
        'items': data['items'],
        'total': data['total'],
        'status': 'pending',
        'createdAt': datetime.utcnow().isoformat()
    }
    orders.insert_one(order)
    return jsonify(order), 201

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['pending', 'processing', 'shipped', 'delivered']:
        return jsonify({'error': 'Invalid status'}), 400
    
    result = orders.update_one(
        {'id': order_id},
        {'$set': {'status': new_status}}
    )
    
    if result.modified_count:
        return jsonify({'success': True, 'status': new_status})
    return jsonify({'error': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)