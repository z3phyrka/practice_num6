import pytest
from src.controllers.payment_strategy import PaymentContext, CreditCardPayment, PayPalPayment
from src.views.notifications import OrderNotifier, EmailNotifier, SMSNotifier
from src.factories.model_factory import FactoryProducer

class TestPatterns:
    """Тестирование паттернов проектирования"""
    
    def test_strategy_pattern(self):
        """Тест стратегии оплаты"""
        context = PaymentContext()
        
        # Тест кредитной карты
        context.set_strategy(CreditCardPayment())
        result = context.execute_payment(1000)
        assert "кредитной картой" in result
        
        # Тест PayPal
        context.set_strategy(PayPalPayment())
        result = context.execute_payment(2000)
        assert "PayPal" in result
    
    def test_observer_pattern(self):
        """Тест наблюдателя"""
        notifier = OrderNotifier()
        email_observer = EmailNotifier()
        sms_observer = SMSNotifier()
        
        notifier.attach(email_observer)
        notifier.attach(sms_observer)
        
        # Проверка уведомлений
        notifier.order_created(123)
    
    def test_factory_pattern(self):
        """Тест фабрики"""
        user_factory = FactoryProducer.get_factory('user')
        user = user_factory.create(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'