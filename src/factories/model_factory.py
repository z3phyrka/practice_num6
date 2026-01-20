from abc import ABC, abstractmethod

class ModelFactory(ABC):
    """Абстрактная фабрика моделей"""
    
    @abstractmethod
    def create(self, **kwargs):
        pass

class UserFactory(ModelFactory):
    """Фабрика пользователей"""
    
    def create(self, **kwargs):
        from src.models.user import User
        return User(
            username=kwargs.get('username'),
            email=kwargs.get('email'),
            password_hash=kwargs.get('password_hash', '')
        )

class ProductFactory(ModelFactory):
    """Фабрика товаров"""
    
    def create(self, **kwargs):
        from src.models.product import Product
        return Product(
            name=kwargs.get('name'),
            description=kwargs.get('description', ''),
            price=kwargs.get('price', 0.0),
            stock=kwargs.get('stock', 0),
            category=kwargs.get('category', ''),
            sku=kwargs.get('sku'),
            image_url=kwargs.get('image_url')
        )

class OrderFactory(ModelFactory):
    """Фабрика заказов"""
    
    def create(self, **kwargs):
        from src.models.order import Order
        return Order(
            user_id=kwargs.get('user_id'),
            total_amount=kwargs.get('total_amount', 0.0),
            shipping_address=kwargs.get('shipping_address'),
            billing_address=kwargs.get('billing_address'),
            payment_method=kwargs.get('payment_method'),
            notes=kwargs.get('notes')
        )

class CartFactory(ModelFactory):
    """Фабрика корзин"""
    
    def create(self, **kwargs):
        from src.models.cart import Cart
        return Cart(
            user_id=kwargs.get('user_id'),
            session_id=kwargs.get('session_id')
        )

class FactoryProducer:
    """Производитель фабрик"""
    
    @staticmethod
    def get_factory(factory_type):
        factories = {
            'user': UserFactory,
            'product': ProductFactory,
            'order': OrderFactory,
            'cart': CartFactory
        }
        
        factory_class = factories.get(factory_type.lower())
        if factory_class:
            return factory_class()
        raise ValueError(f"Unknown factory type: {factory_type}")