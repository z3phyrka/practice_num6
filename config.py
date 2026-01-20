import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация приложения"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # База данных
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ecommerce.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ecommerce')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Очередь сообщений
    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    
    # Микросервисы
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5001')
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://localhost:5002')
    PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://localhost:5003')
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')