from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://mongodb:27017/'))
db = client.shopfront
products = db.products

@app.route('/products', methods=['GET'])
def get_products():
    product_list = list(products.find({}, {'_id': False}))
    return jsonify(product_list)

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = products.find_one({'id': product_id}, {'_id': False})
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    # Initialize some sample products if the collection is empty
    if products.count_documents({}) == 0:
        sample_products = [
            {
                'id': '1',
                'name': 'Premium Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'price': 199.99,
                'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e',
                'category': 'Electronics',
                'stock': 50
            },
            # Add more sample products as needed
        ]
        products.insert_many(sample_products)
    
    app.run(host='0.0.0.0', port=5001)