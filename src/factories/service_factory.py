"""
Factory Pattern для создания сервисов
"""

from abc import ABC, abstractmethod
from src.services.product_service import ProductService
from src.services.order_service import OrderService
from src.services.payment_service import PaymentService
from src.services.notification_service import NotificationService
from src.controllers.payment_strategy import (
    CreditCardPayment, 
    PayPalPayment, 
    CryptoPayment
)

class ServiceFactory(ABC):
    """Абстрактная фабрика сервисов"""
    
    @abstractmethod
    def create_product_service(self):
        pass
    
    @abstractmethod
    def create_order_service(self):
        pass
    
    @abstractmethod
    def create_payment_service(self):
        pass
    
    @abstractmethod
    def create_notification_service(self, config):
        pass

class StandardServiceFactory(ServiceFactory):
    """Стандартная фабрика сервисов"""
    
    def create_product_service(self):
        return ProductService()
    
    def create_order_service(self):
        return OrderService()
    
    def create_payment_service(self):
        from src.services.payment_service import PaymentService
        return PaymentService()
    
    def create_notification_service(self, config):
        return NotificationService(config)

class MockServiceFactory(ServiceFactory):
    """Фабрика для тестирования (возвращает mock-объекты)"""
    
    def create_product_service(self):
        class MockProductService:
            def check_availability(self, product_id, quantity):
                return True
            
            def get_product_with_details(self, product_id):
                return {'id': product_id, 'name': 'Mock Product', 'price': 99.99}
        
        return MockProductService()
    
    def create_order_service(self):
        class MockOrderService:
            def create_order(self, *args, **kwargs):
                return {'id': 1, 'status': 'pending'}
            
            def update_order_status(self, order_id, status):
                return {'id': order_id, 'status': status}
        
        return MockOrderService()
    
    def create_payment_service(self):
        class MockPaymentService:
            def process_payment(self, *args, **kwargs):
                return {'success': True, 'payment_id': 'mock-payment-123'}
        
        return MockPaymentService()
    
    def create_notification_service(self, config):
        class MockNotificationService:
            def send_email(self, *args, **kwargs):
                return True
            
            def update(self, message):
                print(f"Mock notification: {message}")
        
        return MockNotificationService()

class PaymentStrategyFactory:
    """Фабрика для создания стратегий оплаты"""
    
    @staticmethod
    def create_strategy(strategy_type):
        strategies = {
            'credit_card': CreditCardPayment,
            'paypal': PayPalPayment,
            'crypto': CryptoPayment
        }
        
        strategy_class = strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        return strategy_class()

class DatabaseServiceFactory:
    """Фабрика для создания сервисов работы с базами данных"""
    
    @staticmethod
    def create_database_service(db_type):
        if db_type == 'sqlite':
            from src.models.database import DatabaseSingleton
            return DatabaseSingleton()
        elif db_type == 'mongodb':
            class MongoDBService:
                def __init__(self):
                    from pymongo import MongoClient
                    self.client = MongoClient('mongodb://localhost:27017/')
                    self.db = self.client['ecommerce']
                
                def get_collection(self, name):
                    return self.db[name]
            
            return MongoDBService()
        elif db_type == 'postgresql':
            class PostgreSQLService:
                def __init__(self):
                    import psycopg2
                    self.conn = psycopg2.connect(
                        host='localhost',
                        database='ecommerce',
                        user='postgres',
                        password='password'
                    )
            
            return PostgreSQLService()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

class ServiceLocator:
    """
    Service Locator pattern для управления зависимостями
    и предоставления доступа к сервисам
    """
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register_service(cls, name, service):
        """Регистрация сервиса"""
        cls._services[name] = service
    
    @classmethod
    def get_service(cls, name):
        """Получение сервиса по имени"""
        service = cls._services.get(name)
        if service is None:
            raise ValueError(f"Service {name} not found")
        return service
    
    @classmethod
    def create_default_services(cls, config):
        """Создание стандартного набора сервисов"""
        factory = StandardServiceFactory()
        
        cls.register_service('product', factory.create_product_service())
        cls.register_service('order', factory.create_order_service())
        cls.register_service('payment', factory.create_payment_service())
        cls.register_service('notification', factory.create_notification_service(config))
        
        # Регистрация фабрик
        cls.register_service('strategy_factory', PaymentStrategyFactory())
        cls.register_service('db_factory', DatabaseServiceFactory())

# Пример использования
def demonstrate_factory_pattern():
    """Демонстрация работы фабрик"""
    
    # Использование Service Factory
    factory = StandardServiceFactory()
    
    product_service = factory.create_product_service()
    order_service = factory.create_order_service()
    
    print(f"Product Service created: {type(product_service).__name__}")
    print(f"Order Service created: {type(order_service).__name__}")
    
    # Использование Payment Strategy Factory
    strategy_factory = PaymentStrategyFactory()
    credit_card_strategy = strategy_factory.create_strategy('credit_card')
    
    from src.controllers.payment_strategy import PaymentContext
    context = PaymentContext(credit_card_strategy)
    result = context.execute_payment(100)
    print(f"Payment result: {result}")
    
    # Использование Service Locator
    ServiceLocator.create_default_services({})
    
    payment_service = ServiceLocator.get_service('payment')
    print(f"Payment Service from locator: {type(payment_service).__name__}")
    
    return {
        'product_service': product_service,
        'order_service': order_service,
        'payment_strategy': credit_card_strategy,
        'service_locator': ServiceLocator
    }