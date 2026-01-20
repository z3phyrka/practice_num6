from src import db  # Импортируем db из основного модуля

# Импорт моделей
from src.models.user import User
from src.models.product import Product
from src.models.order import Order
from src.models.cart import Cart
from src.models.database import DatabaseSingleton
from src.models.base_model import BaseModel

# Импорт дополнительных моделей
from src.models.order_item import OrderItem
from src.models.cart_item import CartItem

__all__ = [
    'db',  # Добавляем db в экспорт
    'User',
    'Product', 
    'Order',
    'Cart',
    'OrderItem',
    'CartItem',
    'DatabaseSingleton',
    'BaseModel'
]