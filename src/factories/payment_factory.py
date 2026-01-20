from src.controllers.payment_strategy import (
    PaymentStrategy,
    CreditCardPayment,
    PayPalPayment,
    CryptoPayment
)

class PaymentFactory:
    """Фабрика для создания объектов оплаты"""
    
    @staticmethod
    def create_payment(method_type):
        """Создание объекта оплаты по типу"""
        payment_methods = {
            'credit_card': CreditCardPayment,
            'paypal': PayPalPayment,
            'crypto': CryptoPayment
        }
        
        payment_class = payment_methods.get(method_type.lower())
        if payment_class:
            return payment_class()
        
        raise ValueError(f"Unknown payment method: {method_type}")
    
    @staticmethod
    def create_payment_from_config(payment_config):
        """Создание объекта оплаты из конфигурации"""
        method_type = payment_config.get('type', 'credit_card')
        payment = PaymentFactory.create_payment(method_type)
        
        # Установка дополнительных параметров
        if hasattr(payment, 'configure'):
            payment.configure(payment_config)
        
        return payment

class PaymentMethodFactory:
    """Абстрактная фабрика для создания семейств платежных методов"""
    
    def create_processor(self):
        """Создание процессора оплаты"""
        pass
    
    def create_validator(self):
        """Создание валидатора"""
        pass
    
    def create_logger(self):
        """Создание логгера"""
        pass

class CreditCardFactory(PaymentMethodFactory):
    """Фабрика для кредитных карт"""
    
    def create_processor(self):
        return CreditCardProcessor()
    
    def create_validator(self):
        return CreditCardValidator()
    
    def create_logger(self):
        return CreditCardLogger()

class PayPalFactory(PaymentMethodFactory):
    """Фабрика для PayPal"""
    
    def create_processor(self):
        return PayPalProcessor()
    
    def create_validator(self):
        return PayPalValidator()
    
    def create_logger(self):
        return PayPalLogger()

# Примеры классов для фабрики
class CreditCardProcessor:
    def process(self, amount, card_info):
        return f"Processed {amount} via credit card"

class CreditCardValidator:
    def validate(self, card_info):
        return len(card_info.get('number', '')) == 16

class CreditCardLogger:
    def log(self, transaction):
        print(f"Credit card transaction: {transaction}")

class PayPalProcessor:
    def process(self, amount, paypal_info):
        return f"Processed {amount} via PayPal"

class PayPalValidator:
    def validate(self, paypal_info):
        return '@' in paypal_info.get('email', '')

class PayPalLogger:
    def log(self, transaction):
        print(f"PayPal transaction: {transaction}")