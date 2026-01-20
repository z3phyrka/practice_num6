from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    """Абстрактный класс стратегии оплаты"""
    
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    """Оплата кредитной картой"""
    
    def pay(self, amount):
        return f"Оплачено {amount} руб. кредитной картой"

class PayPalPayment(PaymentStrategy):
    """Оплата через PayPal"""
    
    def pay(self, amount):
        return f"Оплачено {amount} руб. через PayPal"

class CryptoPayment(PaymentStrategy):
    """Оплата криптовалютой"""
    
    def pay(self, amount):
        return f"Оплачено {amount} руб. криптовалютой"

class PaymentContext:
    """Контекст для использования стратегий оплаты"""
    
    def __init__(self, strategy: PaymentStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy):
        """Установить стратегию оплаты"""
        self._strategy = strategy
    
    def execute_payment(self, amount):
        """Выполнить оплату с использованием текущей стратегии"""
        if not self._strategy:
            raise ValueError("Стратегия оплаты не установлена")
        return self._strategy.pay(amount)