import { useState, useEffect } from 'react';
import { Product } from '../types';
import { ShoppingCart } from 'lucide-react';
import API_CONFIG from '../config/api';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
}

export default function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const [stock, setStock] = useState<number>(product.stock);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStockLevel();
  }, [product.id]);

  const fetchStockLevel = async () => {
    try {
      const response = await fetch(`${API_CONFIG.STOCK_SERVICE}/stock/${product.id}`);
      if (!response.ok) throw new Error('Failed to fetch stock');
      const data = await response.json();
      setStock(data.quantity);
    } catch (err) {
      console.error('Error fetching stock:', err);
    }
  };

  const handleAddToCart = async () => {
    setLoading(true);
    try {
      // Check current stock before adding to cart
      const response = await fetch(`${API_CONFIG.STOCK_SERVICE}/stock/${product.id}`);
      if (!response.ok) throw new Error('Failed to check stock');
      const { quantity } = await response.json();
      
      if (quantity > 0) {
        // Update stock level
        await fetch(`${API_CONFIG.STOCK_SERVICE}/stock/${product.id}/update`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ quantity: quantity - 1 }),
        });
        
        onAddToCart({ ...product, stock: quantity - 1 });
        setStock(quantity - 1);
      }
    } catch (err) {
      console.error('Error updating stock:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:scale-105">
      <img 
        src={product.image} 
        alt={product.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
        <p className="text-gray-600 text-sm mt-1 line-clamp-2">{product.description}</p>
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xl font-bold text-indigo-600">${product.price}</span>
          <button
            onClick={handleAddToCart}
            disabled={stock === 0 || loading}
            className={`flex items-center space-x-1 px-4 py-2 rounded-md ${
              stock > 0 && !loading
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            <ShoppingCart className="h-4 w-4" />
            <span>
              {loading ? 'Adding...' : stock > 0 ? 'Add to Cart' : 'Out of Stock'}
            </span>
          </button>
        </div>
        <div className="mt-2">
          <span className={`text-sm ${
            stock > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {stock > 0 ? `${stock} in stock` : 'Out of stock'}
          </span>
        </div>
      </div>
    </div>
  );
}