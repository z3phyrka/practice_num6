import hashlib
import string
import random
from datetime import datetime, timedelta
import json

class Helpers:
    """Класс вспомогательных функций"""
    
    @staticmethod
    def generate_token(length=32):
        """Генерация случайного токена"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def hash_password(password, salt=None):
        """Хеширование пароля"""
        if salt is None:
            salt = Helpers.generate_token(16)
        
        # Использование PBKDF2 для хеширования
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password_bytes,
            salt_bytes,
            100000  # Количество итераций
        )
        
        return {
            'hash': hashed.hex(),
            'salt': salt
        }
    
    @staticmethod
    def verify_password(password, stored_hash, salt):
        """Проверка пароля"""
        hashed_password = Helpers.hash_password(password, salt)
        return hashed_password['hash'] == stored_hash
    
    @staticmethod
    def format_price(amount, currency='USD'):
        """Форматирование цены"""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'RUB': '₽'
        }
        
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj, format_str='%Y-%m-%d %H:%M:%S'):
        """Форматирование даты"""
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        
        return date_obj.strftime(format_str)
    
    @staticmethod
    def calculate_discount(original_price, discount_percent):
        """Расчет скидки"""
        discount_amount = original_price * (discount_percent / 100)
        final_price = original_price - discount_amount
        return {
            'original_price': original_price,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'final_price': final_price
        }
    
    @staticmethod
    def paginate(items, page, per_page):
        """Пагинация списка"""
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page
        
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        paginated_items = items[start_index:end_index]
        
        return {
            'items': paginated_items,
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    
    @staticmethod
    def serialize_object(obj):
        """Сериализация объекта в JSON-совместимый формат"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        if hasattr(obj, '__dict__'):
            return {k: Helpers.serialize_object(v) for k, v in obj.__dict__.items() 
                   if not k.startswith('_')}
        
        return obj