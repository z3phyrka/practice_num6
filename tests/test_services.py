"""
Тесты для сервисов и паттернов (Observer, Adapter, Facade, Factory)
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import app, db
from src.services import ProductService, OrderService, PaymentService
from src.services.facade.ecommerce_facade import ECommerceFacade
from src.services.notification_service import NotificationService
from src.api.adapters.payment_adapter import (
    LegacyPaymentSystem, 
    NewPaymentSystem, 
    PaymentAdapter,
    PaymentProcessor
)
from src.api.adapters.shipping_adapter import (
    ShippingAdapter,
    FedExService,
    UPSService
)
from src.factories.service_factory import (
    ServiceFactory,
    StandardServiceFactory,
    MockServiceFactory,
    PaymentStrategyFactory,
    DatabaseServiceFactory,
    ServiceLocator
)
from src.models import User, Product, Order, Cart
from src.views.notifications import (
    Observer,
    Subject,
    EmailNotifier,
    SMSNotifier,
    PushNotifier,
    OrderNotifier
)

class TestObserverPattern:
    """Тесты для Observer паттерна"""
    
    def test_observer_subject(self):
        """Тест Subject (Наблюдаемого объекта)"""
        subject = Subject()
        
        # Создаем мок-наблюдателей
        observer1 = Mock(spec=Observer)
        observer2 = Mock(spec=Observer)
        
        # Подписываем наблюдателей
        subject.attach(observer1)
        subject.attach(observer2)
        
        # Уведомляем наблюдателей
        subject.notify("Test message")
        
        # Проверяем, что наблюдатели получили сообщение
        observer1.update.assert_called_once_with("Test message")
        observer2.update.assert_called_once_with("Test message")
        
        print("✓ Observer: Subject уведомляет всех наблюдателей")
    
    def test_observer_detach(self):
        """Тест отписки наблюдателя"""
        subject = Subject()
        
        observer1 = Mock(spec=Observer)
        observer2 = Mock(spec=Observer)
        
        subject.attach(observer1)
        subject.attach(observer2)
        
        # Отписываем первого наблюдателя
        subject.detach(observer1)
        
        # Уведомляем
        subject.notify("Test message")
        
        # Проверяем
        observer1.update.assert_not_called()
        observer2.update.assert_called_once_with("Test message")
        
        print("✓ Observer: Отписка наблюдателя работает корректно")
    
    def test_order_notifier(self):
        """Тест OrderNotifier (конкретная реализация)"""
        notifier = OrderNotifier()
        
        # Создаем мок-наблюдателей
        email_notifier = Mock(spec=EmailNotifier)
        sms_notifier = Mock(spec=SMSNotifier)
        
        # Подписываем
        notifier.attach(email_notifier)
        notifier.attach(sms_notifier)
        
        # Вызываем методы уведомления
        notifier.order_created(123)
        notifier.order_shipped(456)
        
        # Проверяем, что наблюдатели получили правильные сообщения
        assert email_notifier.update.call_count == 2
        assert sms_notifier.update.call_count == 2
        
        # Проверяем содержание сообщений
        calls = email_notifier.update.call_args_list
        assert "Создан новый заказ #123" in str(calls[0])
        assert "Заказ #456 отправлен" in str(calls[1])
        
        print("✓ Observer: OrderNotifier отправляет правильные уведомления")

class TestAdapterPattern:
    """Тесты для Adapter паттерна"""
    
    def test_legacy_payment_system(self):
        """Тест старой платежной системы"""
        legacy_system = LegacyPaymentSystem()
        result = legacy_system.make_payment(
            customer_id="CUST123",
            invoice_number="INV456",
            amount=1000
        )
        
        assert result['success'] == True
        assert 'transaction_id' in result
        assert result['transaction_id'].startswith('TXCUST123INV456')
        
        print("✓ Adapter: LegacyPaymentSystem работает корректно")
    
    def test_new_payment_system(self):
        """Тест новой платежной системы"""
        new_system = NewPaymentSystem()
        result = new_system.process(
            amount=2000,
            details={'currency': 'USD'}
        )
        
        assert result['success'] == True
        assert 'payment_id' in result
        assert result['amount'] == 2000
        
        print("✓ Adapter: NewPaymentSystem работает корректно")
    
    def test_payment_adapter_legacy(self):
        """Тест адаптера для старой системы"""
        legacy_system = LegacyPaymentSystem()
        adapter = PaymentAdapter(legacy_system)
        
        result = adapter.process(
            amount=1000,
            details={
                'customer_id': 'CUST123',
                'invoice_number': 'INV456'
            }
        )
        
        assert result['success'] == True
        assert 'payment_id' in result
        assert result['amount'] == 1000
        
        print("✓ Adapter: PaymentAdapter работает с LegacyPaymentSystem")
    
    def test_payment_adapter_new(self):
        """Тест адаптера для новой системы"""
        new_system = NewPaymentSystem()
        adapter = PaymentAdapter(new_system)
        
        result = adapter.process(
            amount=2000,
            details={'currency': 'EUR'}
        )
        
        assert result['success'] == True
        assert 'payment_id' in result
        assert result['amount'] == 2000
        
        print("✓ Adapter: PaymentAdapter работает с NewPaymentSystem")
    
    def test_payment_processor(self):
        """Тест процессора платежей с адаптерами"""
        processor = PaymentProcessor()
        
        # Регистрируем адаптеры
        processor.register_adapter('legacy', LegacyPaymentSystem())
        processor.register_adapter('new', NewPaymentSystem())
        
        # Обрабатываем платежи через разные адаптеры
        result1 = processor.process_payment(
            'legacy',
            1000,
            {'customer_id': 'CUST123', 'invoice_number': 'INV001'}
        )
        
        result2 = processor.process_payment(
            'new',
            2000,
            {'currency': 'USD'}
        )
        
        assert result1['success'] == True
        assert result2['success'] == True
        
        print("✓ Adapter: PaymentProcessor управляет несколькими адаптерами")
    
    def test_shipping_adapter(self):
        """Тест адаптера для служб доставки"""
        fedex = FedExService()
        adapter = ShippingAdapter(fedex)
        
        result = adapter.calculate_shipping(
            address='Moscow, Russia',
            weight=2.5,
            dimensions='30x20x15 cm'
        )
        
        assert result['carrier'] == 'FedEx'
        assert 'cost' in result
        assert 'estimated_days' in result
        
        print("✓ Adapter: ShippingAdapter работает с FedExService")

class TestFacadePattern:
    """Тесты для Facade паттерна"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестовых данных
            self.user = User(
                username='facadeuser',
                email='facade@example.com',
                password_hash='hash'
            )
            self.user.save()
            
            self.product = Product(
                name='Facade Product',
                price=150.0,
                category='Test',
                stock=10
            )
            self.product.save()
    
    def teardown_method(self):
        """Очистка тестовых данных"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_facade_initialization(self):
        """Тест инициализации фасада"""
        facade = ECommerceFacade()
        
        assert facade.product_service is not None
        assert facade.order_service is not None
        assert facade.payment_service is not None
        assert facade.notifier is not None
        
        print("✓ Facade: Инициализация работает корректно")
    
    @patch('src.services.facade.ecommerce_facade.ProductService')
    @patch('src.services.facade.ecommerce_facade.OrderService')
    @patch('src.services.facade.ecommerce_facade.PaymentService')
    def test_purchase_product(self, mock_payment, mock_order, mock_product):
        """Тест покупки товара через фасад"""
        # Настройка моков
        mock_product_instance = Mock()
        mock_product_instance.check_availability.return_value = True
        mock_product_instance.get_product_with_details.return_value = Mock(
            id=1, name='Test Product', price=100.0
        )
        mock_product.return_value = mock_product_instance
        
        mock_order_instance = Mock()
        mock_order_instance.create_order.return_value = Mock(
            id=1, total_amount=200.0, status='pending'
        )
        mock_order.return_value = mock_order_instance
        
        mock_payment_instance = Mock()
        mock_payment_instance.process_payment.return_value = {
            'success': True,
            'payment_id': 'PAY123'
        }
        mock_payment.return_value = mock_payment_instance
        
        # Создание фасада
        facade = ECommerceFacade()
        facade.product_service = mock_product_instance
        facade.order_service = mock_order_instance
        facade.payment_service = mock_payment_instance
        
        # Вызов метода фасада
        result = facade.purchase_product(
            user_id=1,
            product_id=1,
            quantity=2,
            payment_method='credit_card'
        )
        
        # Проверка результатов
        assert result['success'] == True
        assert 'order_id' in result['data']
        assert 'payment_id' in result['data']
        
        # Проверка вызовов
        mock_product_instance.check_availability.assert_called_once_with(1, 2)
        mock_order_instance.create_order.assert_called_once()
        mock_payment_instance.process_payment.assert_called_once()
        
        print("✓ Facade: purchase_product работает через единый интерфейс")
    
    def test_facade_error_handling(self):
        """Тест обработки ошибок в фасаде"""
        facade = ECommerceFacade()
        
        # Вызов с неверными параметрами
        result = facade.purchase_product(
            user_id=999,  # Несуществующий пользователь
            product_id=999,  # Несуществующий товар
            quantity=1,
            payment_method='credit_card'
        )
        
        # Должен вернуть ошибку
        assert result['success'] == False
        assert 'error' in result
        
        print("✓ Facade: Обработка ошибок работает корректно")
    
    def test_facade_cache(self):
        """Тест кэширования в фасаде"""
        facade = ECommerceFacade()
        
        # Первый вызов - должен кэшировать
        with patch('src.models.User.get_by_id') as mock_get_user:
            mock_user = Mock(id=1, username='testuser')
            mock_get_user.return_value = mock_user
            
            user1 = facade._get_user(1)
            user2 = facade._get_user(1)
            
            # Должен быть вызван только один раз
            mock_get_user.assert_called_once_with(1)
            assert user1 is user2
            
            print("✓ Facade: Кэширование работает корректно")
    
    def test_facade_clear_cache(self):
        """Тест очистки кэша"""
        facade = ECommerceFacade()
        
        # Добавляем что-то в кэш
        facade._cache['test_key'] = 'test_value'
        assert len(facade._cache) == 1
        
        # Очищаем кэш
        facade.clear_cache()
        assert len(facade._cache) == 0
        
        print("✓ Facade: Очистка кэша работает корректно")

class TestFactoryPattern:
    """Тесты для Factory паттерна"""
    
    def test_standard_service_factory(self):
        """Тест стандартной фабрики сервисов"""
        factory = StandardServiceFactory()
        
        product_service = factory.create_product_service()
        order_service = factory.create_order_service()
        payment_service = factory.create_payment_service()
        
        assert isinstance(product_service, ProductService)
        assert isinstance(order_service, OrderService)
        assert isinstance(payment_service, PaymentService)
        
        print("✓ Factory: StandardServiceFactory создает сервисы корректно")
    
    def test_mock_service_factory(self):
        """Тест мок-фабрики сервисов"""
        factory = MockServiceFactory()
        
        product_service = factory.create_product_service()
        order_service = factory.create_order_service()
        
        # Проверяем мок-методы
        assert product_service.check_availability(1, 1) == True
        assert order_service.create_order(1, [])['status'] == 'pending'
        
        print("✓ Factory: MockServiceFactory создает мок-сервисы")
    
    def test_payment_strategy_factory(self):
        """Тест фабрики стратегий оплаты"""
        factory = PaymentStrategyFactory()
        
        from src.controllers.payment_strategy import (
            CreditCardPayment, 
            PayPalPayment, 
            CryptoPayment
        )
        
        credit_card = factory.create_strategy('credit_card')
        paypal = factory.create_strategy('paypal')
        crypto = factory.create_strategy('crypto')
        
        assert isinstance(credit_card, CreditCardPayment)
        assert isinstance(paypal, PayPalPayment)
        assert isinstance(crypto, CryptoPayment)
        
        print("✓ Factory: PaymentStrategyFactory создает стратегии оплаты")
    
    def test_database_service_factory(self):
        """Тест фабрики сервисов базы данных"""
        factory = DatabaseServiceFactory()
        
        # Тест SQLite сервиса
        sqlite_service = factory.create_database_service('sqlite')
        assert sqlite_service is not None
        
        # Тест MongoDB сервиса
        mongo_service = factory.create_database_service('mongodb')
        assert mongo_service is not None
        
        # Тест ошибки для неизвестного типа
        with pytest.raises(ValueError):
            factory.create_database_service('unknown')
        
        print("✓ Factory: DatabaseServiceFactory создает сервисы БД")
    
    def test_service_locator(self):
        """Тест Service Locator паттерна"""
        # Очистка предыдущих регистраций
        ServiceLocator._services.clear()
        
        # Регистрация сервисов
        ServiceLocator.register_service('test', 'test_service')
        
        # Получение сервиса
        service = ServiceLocator.get_service('test')
        assert service == 'test_service'
        
        # Попытка получить несуществующий сервис
        with pytest.raises(ValueError):
            ServiceLocator.get_service('nonexistent')
        
        # Проверка Singleton
        locator1 = ServiceLocator()
        locator2 = ServiceLocator()
        assert locator1 is locator2
        
        print("✓ Factory: ServiceLocator управляет зависимостями")

class TestServiceIntegration:
    """Интеграционные тесты сервисов"""
    
    def setup_method(self):
        """Настройка тестовых данных"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Создание тестовых данных
            self.user = User(
                username='serviceuser',
                email='service@example.com',
                password_hash='hash'
            )
            self.user.save()
            
            self.product1 = Product(
                name='Service Product 1',
                price=100.0,
                category='Test',
                stock=5
            )
            self.product1.save()
            
            self.product2 = Product(
                name='Service Product 2',
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
    
    def test_product_service_integration(self):
        """Тест интеграции ProductService"""
        with app.app_context():
            service = ProductService()
            
            # Проверка наличия товара
            assert service.check_availability(self.product1.id, 3) == True
            assert service.check_availability(self.product1.id, 10) == False
            
            # Получение товара с деталями
            product = service.get_product_with_details(self.product1.id)
            assert product is not None
            assert product.name == 'Service Product 1'
            
            # Обновление количества
            assert service.update_stock(self.product1.id, -2) == True
            updated_product = Product.get_by_id(self.product1.id)
            assert updated_product.stock == 3  # Было 5, стало 3
            
            print("✓ Service: ProductService интегрируется с моделями")
    
    def test_order_service_integration(self):
        """Тест интеграции OrderService"""
        with app.app_context():
            service = OrderService()
            
            # Создание заказа
            order = service.create_order(
                user_id=self.user.id,
                items_data=[
                    {
                        'product_id': self.product1.id,
                        'quantity': 2,
                        'price': self.product1.price
                    }
                ]
            )
            
            # Проверка
            assert order.id is not None
            assert order.user_id == self.user.id
            
            # Обновление статуса
            updated_order = service.update_order_status(order.id, 'shipped')
            assert updated_order.status == 'shipped'
            
            # Отмена заказа
            cancelled_order = service.cancel_order(order.id)
            assert cancelled_order.status == 'cancelled'
            
            # Проверка возврата товара на склад
            product_after = Product.get_by_id(self.product1.id)
            assert product_after.stock == 5  # Должно вернуться к исходному
            
            print("✓ Service: OrderService интегрируется с моделями")
    
    def test_payment_service_integration(self):
        """Тест интеграции PaymentService"""
        service = PaymentService()
        
        # Обработка платежа
        result = service.process_payment(
            order_id=1,
            amount=1000,
            payment_method='credit_card'
        )
        
        assert result['success'] == True
        assert 'payment_id' in result
        
        # Возврат платежа
        refund_result = service.refund_payment(
            payment_id='PAY123',
            amount=500
        )
        
        assert refund_result['success'] == True
        assert 'refund_id' in refund_result
        
        print("✓ Service: PaymentService обрабатывает платежи")
    
    @patch('smtplib.SMTP')
    def test_notification_service_integration(self, mock_smtp):
        """Тест интеграции NotificationService"""
        # Настройка мока SMTP
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Конфигурация
        config = {
            'MAIL_SERVER': 'smtp.gmail.com',
            'MAIL_PORT': 587,
            'MAIL_USERNAME': 'test@example.com',
            'MAIL_PASSWORD': 'password'
        }
        
        service = NotificationService(config)
        
        # Отправка email
        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        # В тестовом режиме должно вернуть True
        assert result == True
        
        # Проверка Observer интерфейса
        service.update("Test message")
        
        print("✓ Service: NotificationService отправляет уведомления")

class TestPatternDemonstration:
    """Демонстрация работы всех паттернов"""
    
    def test_all_patterns_demo(self):
        """Демонстрация всех паттернов в одном тесте"""
        print("\n" + "="*60)
        print("Демонстрация архитектурных паттернов")
        print("="*60)
        
        # 1. Singleton Pattern
        print("\n1. Singleton Pattern:")
        from src.models.database import DatabaseSingleton
        db1 = DatabaseSingleton()
        db2 = DatabaseSingleton()
        print(f"   DatabaseSingleton одинаковы: {db1 is db2}")
        
        # 2. Factory Pattern
        print("\n2. Factory Pattern:")
        from src.factories.service_factory import StandardServiceFactory
        factory = StandardServiceFactory()
        product_service = factory.create_product_service()
        print(f"   Создан ProductService: {type(product_service).__name__}")
        
        # 3. Observer Pattern
        print("\n3. Observer Pattern:")
        from src.views.notifications import OrderNotifier, EmailNotifier
        notifier = OrderNotifier()
        email_observer = EmailNotifier()
        notifier.attach(email_observer)
        print(f"   Observers attached: {len(notifier._observers)}")
        
        # 4. Strategy Pattern
        print("\n4. Strategy Pattern:")
        from src.controllers.payment_strategy import PaymentContext, CreditCardPayment
        context = PaymentContext(CreditCardPayment())
        result = context.execute_payment(1000)
        print(f"   Payment result: {result[:30]}...")
        
        # 5. Adapter Pattern
        print("\n5. Adapter Pattern:")
        from src.api.adapters.payment_adapter import LegacyPaymentSystem, PaymentAdapter
        legacy = LegacyPaymentSystem()
        adapter = PaymentAdapter(legacy)
        result = adapter.process(1000, {'customer_id': 'TEST'})
        print(f"   Adapter result success: {result['success']}")
        
        # 6. Facade Pattern
        print("\n6. Facade Pattern:")
        facade = ECommerceFacade()
        print(f"   Facade initialized with {len(facade._cache)} cached items")
        
        # 7. Service Locator
        print("\n7. Service Locator:")
        from src.factories.service_factory import ServiceLocator
        ServiceLocator.register_service('demo', 'demo_service')
        service = ServiceLocator.get_service('demo')
        print(f"   Service from locator: {service}")
        
        print("\n" + "="*60)
        print("Демонстрация завершена!")
        print("="*60)

if __name__ == '__main__':
    # Запуск тестов с выводом результатов
    print("="*60)
    print("Запуск тестов сервисов и паттернов")
    print("="*60)
    
    # Создаем тестовый runner
    test_classes = [
        TestObserverPattern(),
        TestAdapterPattern(),
        TestFacadePattern(),
        TestFactoryPattern(),
        TestServiceIntegration(),
        TestPatternDemonstration()
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
            
            # Устанавливаем контекст приложения для тестов сервисов
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