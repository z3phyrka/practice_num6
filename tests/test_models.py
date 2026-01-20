"""
Тесты для моделей и Singleton паттерна
"""

import pytest
import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import app, db
from src.models import User, Product, Order, Cart, DatabaseSingleton
from src.factories.model_factory import UserFactory, ProductFactory, FactoryProducer

class TestSingletonPattern:
    """Тесты для Singleton паттерна"""
    
    def test_database_singleton(self):
        """Тест что DatabaseSingleton возвращает один и тот же экземпляр"""
        # Первый вызов
        db1 = DatabaseSingleton()
        
        # Второй вызов
        db2 = DatabaseSingleton()
        
        # Третий вызов
        db3 = DatabaseSingleton()
        
        # Все три переменные должны ссылаться на один объект
        assert db1 is db2, "db1 и db2 должны быть одним экземпляром"
        assert db2 is db3, "db2 и db3 должны быть одним экземпляром"
        assert db1 is db3, "db1 и db3 должны быть одним экземпляром"
        
        print("✓ Singleton: Все экземпляры DatabaseSingleton одинаковы")
    
    def test_singleton_connection(self):
        """Тест подключений Singleton"""
        db = DatabaseSingleton()
        
        # Проверка SQLite соединения
        conn = db.get_sqlite_connection()
        assert conn is not None, "SQLite соединение не должно быть None"
        
        # Проверка MongoDB коллекции
        collection = db.get_mongo_collection('test')
        assert collection is not None, "MongoDB коллекция не должна быть None"
        
        # Проверка Redis клиента
        redis = db.get_redis_client()
        assert redis is not None, "Redis клиент не должен быть None"
        
        print("✓ Singleton: Все подключения инициализированы")

class TestModels:
    """Тесты для моделей данных"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создание тестового приложения
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_model(self):
        """Тест модели пользователя"""
        with app.app_context():
            # Создание пользователя
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hashed_password'
            )
            
            # Сохранение
            db.session.add(user)
            db.session.commit()
            
            # Проверка
            assert user.id is not None, "ID должен быть установлен"
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.created_at is not None
            
            # Проверка CRUD операций
            # Чтение
            saved_user = User.get_by_id(user.id)
            assert saved_user is not None
            assert saved_user.username == 'testuser'
            
            # Обновление
            user.update(username='updateduser')
            assert user.username == 'updateduser'
            
            # Удаление
            user.delete()
            deleted_user = User.get_by_id(user.id)
            assert deleted_user is None
            
            print("✓ User Model: CRUD операции работают корректно")
    
    def test_product_model(self):
        """Тест модели товара"""
        with app.app_context():
            # Создание товара
            product = Product(
                name='Test Product',
                description='Test Description',
                price=99.99,
                category='Electronics',
                stock=10,
                sku='TEST-001'
            )
            
            product.save()
            
            # Проверка
            assert product.id is not None
            assert product.name == 'Test Product'
            assert product.price == 99.99
            assert product.stock == 10
            
            # Проверка методов
            # Уменьшение количества
            assert product.reduce_stock(5) == True
            assert product.stock == 5
            
            # Попытка уменьшить больше чем есть
            assert product.reduce_stock(10) == False
            assert product.stock == 5
            
            # Увеличение количества
            product.increase_stock(10)
            assert product.stock == 15
            
            print("✓ Product Model: Методы работы с товаром работают корректно")
    
    def test_order_model(self):
        """Тест модели заказа"""
        with app.app_context():
            # Создание пользователя для заказа
            user = User(
                username='orderuser',
                email='order@example.com',
                password_hash='hashed'
            )
            user.save()
            
            # Создание товара
            product = Product(
                name='Order Product',
                price=50.0,
                category='Test',
                stock=5
            )
            product.save()
            
            # Создание заказа
            order = Order.create(
                user_id=user.id,
                items_data=[
                    {
                        'product_id': product.id,
                        'quantity': 2,
                        'price': product.price
                    }
                ]
            )
            
            # Проверка
            assert order.id is not None
            assert order.user_id == user.id
            assert order.total_amount == 100.0
            assert order.status == 'pending'
            assert len(order.items) == 1
            assert order.items[0].product_id == product.id
            
            # Проверка обновления статуса
            order.update_status('paid')
            assert order.status == 'paid'
            
            print("✓ Order Model: Создание и обновление заказа работает корректно")
    
    def test_cart_model(self):
        """Тест модели корзины"""
        with app.app_context():
            # Создание пользователя
            user = User(
                username='cartuser',
                email='cart@example.com',
                password_hash='hashed'
            )
            user.save()
            
            # Создание товара
            product = Product(
                name='Cart Product',
                price=25.0,
                category='Test',
                stock=10
            )
            product.save()
            
            # Создание корзины
            cart = Cart(user_id=user.id)
            cart.save()
            
            # Добавление товара в корзину
            cart.add_item(product.id, 3)
            
            # Проверка
            assert cart.id is not None
            assert len(cart.items) == 1
            assert cart.items[0].product_id == product.id
            assert cart.items[0].quantity == 3
            assert cart.get_total() == 75.0
            assert cart.get_item_count() == 3
            
            # Обновление количества
            cart.update_item_quantity(product.id, 5)
            assert cart.items[0].quantity == 5
            
            # Удаление товара
            cart.remove_item(product.id)
            assert len(cart.items) == 0
            
            print("✓ Cart Model: Работа с корзиной работает корректно")

class TestFactoryPattern:
    """Тесты для Factory паттерна"""
    
    def test_user_factory(self):
        """Тест фабрики пользователей"""
        factory = UserFactory()
        user = factory.create(
            username='factoryuser',
            email='factory@example.com',
            password_hash='factory_hash'
        )
        
        assert user.username == 'factoryuser'
        assert user.email == 'factory@example.com'
        assert user.password_hash == 'factory_hash'
        
        print("✓ Factory: UserFactory создает пользователей корректно")
    
    def test_product_factory(self):
        """Тест фабрики товаров"""
        factory = ProductFactory()
        product = factory.create(
            name='Factory Product',
            description='Made by factory',
            price=199.99,
            stock=50,
            category='Factory'
        )
        
        assert product.name == 'Factory Product'
        assert product.price == 199.99
        assert product.stock == 50
        assert product.category == 'Factory'
        
        print("✓ Factory: ProductFactory создает товары корректно")
    
    def test_factory_producer(self):
        """Тест производителя фабрик"""
        # Получение фабрики пользователей
        user_factory = FactoryProducer.get_factory('user')
        assert isinstance(user_factory, UserFactory)
        
        # Получение фабрики товаров
        product_factory = FactoryProducer.get_factory('product')
        assert isinstance(product_factory, ProductFactory)
        
        # Попытка получить несуществующую фабрику
        with pytest.raises(ValueError):
            FactoryProducer.get_factory('unknown')
        
        print("✓ FactoryProducer: Возвращает правильные фабрики")

class TestModelRelationships:
    """Тесты для связей между моделями"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестовых данных
            self.user = User(
                username='relationuser',
                email='relation@example.com',
                password_hash='hash'
            )
            self.user.save()
            
            self.product = Product(
                name='Relation Product',
                price=100.0,
                category='Test',
                stock=10
            )
            self.product.save()
    
    def teardown_method(self):
        """Очистка тестовых данных"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_cart_relationship(self):
        """Тест связи пользователь-корзина"""
        with app.app_context():
            # Создание корзины для пользователя
            cart = Cart(user_id=self.user.id)
            cart.save()
            
            # Проверка связи
            assert cart.user_id == self.user.id
            assert self.user.cart is not None
            assert self.user.cart.id == cart.id
            
            print("✓ Relationships: Связь User-Cart работает корректно")
    
    def test_user_orders_relationship(self):
        """Тест связи пользователь-заказы"""
        with app.app_context():
            # Создание заказа
            order = Order.create(
                user_id=self.user.id,
                items_data=[
                    {
                        'product_id': self.product.id,
                        'quantity': 1,
                        'price': self.product.price
                    }
                ]
            )
            
            # Проверка связи
            assert order.user_id == self.user.id
            assert len(self.user.orders) == 1
            assert self.user.orders[0].id == order.id
            
            print("✓ Relationships: Связь User-Order работает корректно")
    
    def test_order_items_relationship(self):
        """Тест связи заказ-товары"""
        with app.app_context():
            # Создание заказа
            order = Order.create(
                user_id=self.user.id,
                items_data=[
                    {
                        'product_id': self.product.id,
                        'quantity': 2,
                        'price': self.product.price
                    }
                ]
            )
            
            # Проверка связи
            assert len(order.items) == 1
            assert order.items[0].product_id == self.product.id
            assert order.items[0].order_id == order.id
            assert order.items[0].quantity == 2
            
            print("✓ Relationships: Связь Order-Product работает корректно")

if __name__ == '__main__':
    # Запуск тестов с выводом результатов
    print("="*60)
    print("Запуск тестов моделей и паттернов")
    print("="*60)
    
    # Создаем тестовый runner
    test_classes = [
        TestSingletonPattern(),
        TestModels(),
        TestFactoryPattern(),
        TestModelRelationships()
    ]
    
    # Запускаем тесты
    for test_class in test_classes:
        print(f"\nТестирование: {test_class.__class__.__name__}")
        print("-"*40)
        
        # Получаем все методы тестирования
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            method = getattr(test_class, method_name)
            
            # Устанавливаем контекст приложения для тестов моделей
            if hasattr(test_class, 'setup_method'):
                test_class.setup_method()
            
            try:
                method()
                print(f"  ✓ {method_name}")
            except Exception as e:
                print(f"  ✗ {method_name}: {str(e)}")
            finally:
                # Очищаем после теста
                if hasattr(test_class, 'teardown_method'):
                    test_class.teardown_method()
    
    print("\n" + "="*60)
    print("Тестирование завершено!")
    print("="*60)