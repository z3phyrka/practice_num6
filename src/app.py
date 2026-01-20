from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import threading
import queue
import time
from datetime import datetime

# Инициализация Flask приложения
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db = SQLAlchemy(app)

# Для миграций можно использовать Alembic, но для простоты уберем Flask-Migrate
# Вместо этого добавим простую инициализацию базы данных
def init_database():
    """Инициализация базы данных"""
    with app.app_context():
        from src.models import User, Product, Order, Cart, OrderItem, CartItem
        db.create_all()
        
        # Создание демо-данных
        if not User.query.first():
            demo_user = User(
                username='demo',
                email='demo@example.com',
                password_hash='demo123'
            )
            db.session.add(demo_user)
            
            demo_product = Product(
                name='Демо товар',
                description='Это демонстрационный товар',
                price=99.99,
                category='Электроника',
                stock=10,
                sku='DEMO-001'
            )
            db.session.add(demo_product)
            
            db.session.commit()
            print("Демо данные созданы")

# Очередь для Producer-Consumer pattern
task_queue = queue.Queue()
result_queue = queue.Queue()

# Импорт после инициализации приложения
from src.models import User, Product, Order, Cart
from src.controllers import UserController, ProductController, OrderController, CartController
from src.api.routes import init_routes
from src.utils.producers_consumers import Producer, Consumer

def init_app():
    """Инициализация приложения"""
    # Инициализация базы данных
    init_database()
    
    # Регистрация маршрутов
    init_routes(app)
    
    # Запуск Producer-Consumer потоков (опционально, для демонстрации)
    try:
        producer = Producer(task_queue)
        consumer = Consumer(task_queue, result_queue)
        
        producer_thread = threading.Thread(target=producer.run, daemon=True)
        consumer_thread = threading.Thread(target=consumer.run, daemon=True)
        
        producer_thread.start()
        consumer_thread.start()
        print("Producer-Consumer потоки запущены")
    except Exception as e:
        print(f"Ошибка при запуске потоков: {e}")
    
    return app

@app.route('/')
def index():
    """Главная страница"""
    return "Добро пожаловать в онлайн-магазин!"

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    return {
        'status': 'healthy',
        'service': 'ecommerce-store',
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    app = init_app()
    print(f"Приложение запущено на http://localhost:5000")
    app.run(debug=True, port=5000)