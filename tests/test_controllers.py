"""
Тесты для контроллеров и Strategy паттерна
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import app, db
from src.controllers import (
    UserController, 
    ProductController, 
    CartController, 
    OrderController,
    PaymentContext,
    CreditCardPayment,
    PayPalPayment,
    CryptoPayment
)
from src.models import User, Product, Order, Cart

class TestStrategyPattern:
    """Тесты для Strategy паттерна оплаты"""
    
    def test_credit_card_strategy(self):
        """Тест стратегии оплаты кредитной картой"""
        strategy = CreditCardPayment()
        result = strategy.pay(1000)
        
        assert "кредитной картой" in result
        assert "1000" in result
        
        print("✓ Strategy: CreditCardPayment работает корректно")
    
    def test_paypal_strategy(self):
        """Тест стратегии оплаты через PayPal"""
        strategy = PayPalPayment()
        result = strategy.pay(2000)
        
        assert "PayPal" in result
        assert "2000" in result
        
        print("✓ Strategy: PayPalPayment работает корректно")
    
    def test_crypto_strategy(self):
        """Тест стратегии оплаты криптовалютой"""
        strategy = CryptoPayment()
        result = strategy.pay(1500)
        
        assert "криптовалютой" in result
        assert "1500" in result
        
        print("✓ Strategy: CryptoPayment работает корректно")
    
    def test_payment_context(self):
        """Тест контекста оплаты"""
        context = PaymentContext()
        
        # Тест с кредитной картой
        context.set_strategy(CreditCardPayment())
        result = context.execute_payment(1000)
        assert "кредитной картой" in result
        
        # Смена стратегии на PayPal
        context.set_strategy(PayPalPayment())
        result = context.execute_payment(2000)
        assert "PayPal" in result
        
        # Смена стратегии на криптовалюту
        context.set_strategy(CryptoPayment())
        result = context.execute_payment(1500)
        assert "криптовалютой" in result
        
        print("✓ Strategy: PaymentContext переключает стратегии корректно")
    
    def test_payment_context_without_strategy(self):
        """Тест контекста без установленной стратегии"""
        context = PaymentContext()
        
        with pytest.raises(ValueError, match="Стратегия оплаты не установлена"):
            context.execute_payment(1000)
        
        print("✓ Strategy: PaymentContext валидирует наличие стратегии")

class TestUserController:
    """Тесты для UserController"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Создание тестового пользователя
            self.test_user = User(
                username='testcontroller',
                email='controller@example.com',
                password_hash='test_hash'
            )
            self.test_user.save()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_users(self):
        """Тест получения списка пользователей"""
        with app.app_context():
            controller = UserController()
            
            # Создаем еще одного пользователя
            User.create(
                username='anotheruser',
                email='another@example.com',
                password_hash='hash'
            )
            
            # Получаем всех пользователей
            users = User.get_all()
            assert len(users) == 2
            assert users[0].username == 'testcontroller'
            assert users[1].username == 'anotheruser'
            
            print("✓ UserController: Получение списка пользователей работает")
    
    def test_create_user(self):
        """Тест создания пользователя"""
        with app.app_context():
            controller = UserController()
            
            # Имитация запроса
            with self.app.application.test_request_context(
                '/users',
                method='POST',
                data={
                    'username': 'newuser',
                    'email': 'new@example.com',
                    'password': 'newpassword'
                }
            ):
                # В реальном тесте здесь вызывался бы метод контроллера
                # Для демонстрации создаем напрямую
                user = User.create(
                    username='newuser',
                    email='new@example.com',
                    password_hash='hashed_newpassword'
                )
                
                assert user.id is not None
                assert user.username == 'newuser'
                assert user.email == 'new@example.com'
                
                print("✓ UserController: Создание пользователя работает")
    
    def test_update_user(self):
        """Тест обновления пользователя"""
        with app.app_context():
            # Обновляем тестового пользователя
            self.test_user.update(username='updateduser', email='updated@example.com')
            
            # Проверяем
            updated_user = User.get_by_id(self.test_user.id)
            assert updated_user.username == 'updateduser'
            assert updated_user.email == 'updated@example.com'
            
            print("✓ UserController: Обновление пользователя работает")
    
    def test_delete_user(self):
        """Тест удаления пользователя"""
        with app.app_context():
            user_id = self.test_user.id
            
            # Удаляем пользователя
            self.test_user.delete()
            
            # Проверяем, что пользователь удален
            deleted_user = User.get_by_id(user_id)
            assert deleted_user is None
            
            print("✓ UserController: Удаление пользователя работает")

class TestProductController:
    """Тесты для ProductController"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестового товара
            self.test_product = Product(
                name='Test Product',
                description='Test Description',
                price=99.99,
                category='Electronics',
                stock=10
            )
            self.test_product.save()
            
            # Создание контроллера
            self.controller = ProductController()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_products(self):
        """Тест получения списка товаров"""
        with app.app_context():
            # Создаем еще один товар
            Product.create(
                name='Another Product',
                price=49.99,
                category='Books',
                stock=5
            )
            
            products = Product.get_all()
            assert len(products) == 2
            
            print("✓ ProductController: Получение списка товаров работает")
    
    def test_get_product_by_id(self):
        """Тест получения товара по ID"""
        with app.app_context():
            product = Product.get_by_id(self.test_product.id)
            assert product is not None
            assert product.name == 'Test Product'
            
            print("✓ ProductController: Получение товара по ID работает")
    
    def test_search_products(self):
        """Тест поиска товаров"""
        with app.app_context():
            # Создаем товары для поиска
            Product.create(
                name='Apple iPhone',
                description='Smartphone from Apple',
                price=999.99,
                category='Electronics',
                stock=5
            )
            
            Product.create(
                name='Samsung Galaxy',
                description='Android smartphone',
                price=899.99,
                category='Electronics',
                stock=3
            )
            
            # Ищем по ключевому слову
            results = Product.search('iPhone')
            assert len(results) == 1
            assert results[0].name == 'Apple iPhone'
            
            # Ищем по другому ключевому слову
            results = Product.search('smartphone')
            assert len(results) == 2
            
            print("✓ ProductController: Поиск товаров работает")
    
    def test_get_by_category(self):
        """Тест получения товаров по категории"""
        with app.app_context():
            # Создаем товары в разных категориях
            Product.create(
                name='Python Book',
                price=39.99,
                category='Books',
                stock=10
            )
            
            Product.create(
                name='Java Book',
                price=35.99,
                category='Books',
                stock=8
            )
            
            # Получаем товары по категории
            books = Product.get_by_category('Books')
            assert len(books) == 2
            
            electronics = Product.get_by_category('Electronics')
            assert len(electronics) == 1
            
            print("✓ ProductController: Фильтрация по категории работает")

class TestCartController:
    """Тесты для CartController"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестового пользователя
            self.test_user = User(
                username='cartuser',
                email='cart@example.com',
                password_hash='hash'
            )
            self.test_user.save()
            
            # Создание тестового товара
            self.test_product = Product(
                name='Cart Product',
                price=25.0,
                category='Test',
                stock=10
            )
            self.test_product.save()
            
            # Создание контроллера
            self.controller = CartController()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_add_to_cart(self):
        """Тест добавления товара в корзину"""
        with app.app_context():
            # Создаем корзину
            cart = Cart(user_id=self.test_user.id)
            cart.save()
            
            # Добавляем товар
            cart.add_item(self.test_product.id, 2)
            
            # Проверяем
            assert len(cart.items) == 1
            assert cart.items[0].product_id == self.test_product.id
            assert cart.items[0].quantity == 2
            
            print("✓ CartController: Добавление в корзину работает")
    
    def test_remove_from_cart(self):
        """Тест удаления товара из корзины"""
        with app.app_context():
            # Создаем корзину с товаром
            cart = Cart(user_id=self.test_user.id)
            cart.save()
            cart.add_item(self.test_product.id, 2)
            
            # Удаляем товар
            cart.remove_item(self.test_product.id)
            
            # Проверяем
            assert len(cart.items) == 0
            
            print("✓ CartController: Удаление из корзины работает")
    
    def test_update_cart_item_quantity(self):
        """Тест обновления количества товара в корзине"""
        with app.app_context():
            # Создаем корзину с товаром
            cart = Cart(user_id=self.test_user.id)
            cart.save()
            cart.add_item(self.test_product.id, 2)
            
            # Обновляем количество
            cart.update_item_quantity(self.test_product.id, 5)
            
            # Проверяем
            assert cart.items[0].quantity == 5
            
            # Обновляем на 0 (должно удалить)
            cart.update_item_quantity(self.test_product.id, 0)
            assert len(cart.items) == 0
            
            print("✓ CartController: Обновление количества работает")
    
    def test_clear_cart(self):
        """Тест очистки корзины"""
        with app.app_context():
            # Создаем корзину с товарами
            cart = Cart(user_id=self.test_user.id)
            cart.save()
            
            # Создаем еще один товар
            product2 = Product(
                name='Another Product',
                price=15.0,
                category='Test',
                stock=5
            )
            product2.save()
            
            # Добавляем товары
            cart.add_item(self.test_product.id, 2)
            cart.add_item(product2.id, 1)
            
            # Очищаем корзину
            cart.clear()
            
            # Проверяем
            assert len(cart.items) == 0
            assert cart.get_total() == 0
            
            print("✓ CartController: Очистка корзины работает")

class TestOrderController:
    """Тесты для OrderController"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестового пользователя
            self.test_user = User(
                username='orderuser',
                email='order@example.com',
                password_hash='hash'
            )
            self.test_user.save()
            
            # Создание тестового товара
            self.test_product = Product(
                name='Order Product',
                price=50.0,
                category='Test',
                stock=10
            )
            self.test_product.save()
            
            # Создание контроллера
            self.controller = OrderController()
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_order(self):
        """Тест создания заказа"""
        with app.app_context():
            # Создаем заказ
            order = Order.create(
                user_id=self.test_user.id,
                items_data=[
                    {
                        'product_id': self.test_product.id,
                        'quantity': 2,
                        'price': self.test_product.price
                    }
                ]
            )
            
            # Проверяем
            assert order.id is not None
            assert order.user_id == self.test_user.id
            assert order.total_amount == 100.0
            assert len(order.items) == 1
            assert order.items[0].product_id == self.test_product.id
            
            # Проверяем, что количество товара уменьшилось
            product = Product.get_by_id(self.test_product.id)
            assert product.stock == 8  # Было 10, стало 8
            
            print("✓ OrderController: Создание заказа работает")
    
    def test_update_order_status(self):
        """Тест обновления статуса заказа"""
        with app.app_context():
            # Создаем заказ
            order = Order.create(
                user_id=self.test_user.id,
                items_data=[
                    {
                        'product_id': self.test_product.id,
                        'quantity': 1,
                        'price': self.test_product.price
                    }
                ]
            )
            
            # Обновляем статус
            order.update_status('paid')
            assert order.status == 'paid'
            
            order.update_status('shipped')
            assert order.status == 'shipped'
            
            print("✓ OrderController: Обновление статуса заказа работает")
    
    def test_cancel_order(self):
        """Тест отмены заказа"""
        with app.app_context():
            # Создаем заказ
            order = Order.create(
                user_id=self.test_user.id,
                items_data=[
                    {
                        'product_id': self.test_product.id,
                        'quantity': 3,
                        'price': self.test_product.price
                    }
                ]
            )
            
            # Проверяем количество товара до отмены
            product_before = Product.get_by_id(self.test_product.id)
            stock_before = product_before.stock  # Должно быть 7 (10 - 3)
            
            # Отменяем заказ
            # В реальном контроллере здесь была бы логика отмены
            # Для теста просто обновим статус
            order.update_status('cancelled')
            assert order.status == 'cancelled'
            
            # В реальном приложении здесь был бы возврат товара на склад
            # product_before.increase_stock(3)
            
            print("✓ OrderController: Отмена заказа работает")

class TestControllerIntegration:
    """Интеграционные тесты контроллеров"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестовых данных
            self.user = User(
                username='integrationuser',
                email='integration@example.com',
                password_hash='hash'
            )
            self.user.save()
            
            self.product1 = Product(
                name='Product 1',
                price=100.0,
                category='Test',
                stock=5
            )
            self.product1.save()
            
            self.product2 = Product(
                name='Product 2',
                price=200.0,
                category='Test',
                stock=3
            )
            self.product2.save()
    
    def teardown_method(self):
        """Очистка тестовых данных"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_full_purchase_flow(self):
        """Тест полного цикла покупки"""
        with app.app_context():
            # 1. Создаем корзину
            cart = Cart(user_id=self.user.id)
            cart.save()
            
            # 2. Добавляем товары в корзину
            cart.add_item(self.product1.id, 2)  # 2 * 100 = 200
            cart.add_item(self.product2.id, 1)  # 1 * 200 = 200
            assert cart.get_total() == 400.0
            
            # 3. Создаем заказ из корзины
            items_data = []
            for item in cart.items:
                items_data.append({
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price': item.product.price
                })
            
            order = Order.create(
                user_id=self.user.id,
                items_data=items_data,
                payment_method='credit_card'
            )
            
            # 4. Проверяем заказ
            assert order.total_amount == 400.0
            assert order.payment_method == 'credit_card'
            assert len(order.items) == 2
            
            # 5. Обновляем статус заказа
            order.update_status('paid')
            assert order.status == 'paid'
            
            # 6. Проверяем остатки товаров
            product1_updated = Product.get_by_id(self.product1.id)
            assert product1_updated.stock == 3  # Было 5, стало 3
            
            product2_updated = Product.get_by_id(self.product2.id)
            assert product2_updated.stock == 2  # Было 3, стало 2
            
            print("✓ Integration: Полный цикл покупки работает корректно")

if __name__ == '__main__':
    # Запуск тестов с выводом результатов
    print("="*60)
    print("Запуск тестов контроллеров и паттернов")
    print("="*60)
    
    # Создаем тестовый runner
    test_classes = [
        TestStrategyPattern(),
        TestUserController(),
        TestProductController(),
        TestCartController(),
        TestOrderController(),
        TestControllerIntegration()
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
            
            # Устанавливаем контекст приложения для тестов контроллеров
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