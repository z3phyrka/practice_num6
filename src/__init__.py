"""
E-commerce Store Application
Применение архитектурных паттернов проектирования в системе управления онлайн-магазином
"""

__version__ = '1.0.0'
__author__ = 'Student Project'
__description__ = 'Система управления онлайн-магазином с применением MVC, микросервисов и паттернов проектирования'

# Создаем экземпляры основных компонентов
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

# Инициализация приложения
def create_app(config_class=None):
    """Фабрика приложения"""
    if config_class:
        app.config.from_object(config_class)
    
    # Инициализация базы данных
    db.init_app(app)
    
    # Регистрация маршрутов
    from src.api.routes import init_routes
    init_routes(app)
    
    return app

# Экспорт основных компонентов
from src.models import User, Product, Order, Cart
from src.controllers import UserController, ProductController, OrderController, CartController

__all__ = [
    'app',
    'db',
    'create_app',
    'User',
    'Product',
    'Order',
    'Cart',
    'UserController',
    'ProductController',
    'OrderController',
    'CartController'
]