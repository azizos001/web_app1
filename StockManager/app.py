from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client.shopfront
stock = db.stock

@app.route('/stock/<product_id>', methods=['GET'])
def get_stock(product_id):
    stock_info = stock.find_one({'product_id': product_id}, {'_id': False})
    if not stock_info:
        # Initialize stock if it doesn't exist
        stock_info = {
            'product_id': product_id,
            'quantity': 50  # Default initial stock
        }
        stock.insert_one(stock_info)
    return jsonify(stock_info)

@app.route('/stock/<product_id>/update', methods=['POST'])
def update_stock(product_id):
    data = request.get_json()
    new_quantity = data.get('quantity', 0)
    
    if new_quantity < 0:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    result = stock.update_one(
        {'product_id': product_id},
        {'$set': {'quantity': new_quantity}},
        upsert=True
    )
    
    # Notify when stock is low (less than 10 items)
    if new_quantity < 10:
        print(f"Low stock alert for product {product_id}: {new_quantity} items remaining")
    
    return jsonify({
        'success': True,
        'product_id': product_id,
        'quantity': new_quantity
    })

@app.route('/stock/batch', methods=['POST'])
def batch_update_stock():
    updates = request.get_json()
    results = []
    
    for update in updates:
        product_id = update.get('product_id')
        quantity = update.get('quantity')
        
        if product_id and quantity is not None:
            stock.update_one(
                {'product_id': product_id},
                {'$set': {'quantity': quantity}},
                upsert=True
            )
            results.append({
                'product_id': product_id,
                'quantity': quantity,
                'status': 'updated'
            })
    
    return jsonify(results)

if __name__ == '__main__':
    # Initialize sample stock data if collection is empty
    if stock.count_documents({}) == 0:
        sample_stock = [
            {'product_id': '1', 'quantity': 50},
            {'product_id': '2', 'quantity': 30},
            {'product_id': '3', 'quantity': 20},
        ]
        stock.insert_many(sample_stock)
    
    app.run(host='0.0.0.0', port=5002)