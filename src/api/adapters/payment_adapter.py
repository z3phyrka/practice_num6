"""
Adapter Pattern для интеграции различных платежных систем
"""

import time
from abc import ABC, abstractmethod

class PaymentSystem(ABC):
    """Абстрактный класс платежной системы"""
    
    @abstractmethod
    def process(self, amount, details):
        pass
    
    @abstractmethod
    def refund(self, transaction_id, amount):
        pass

class LegacyPaymentSystem:
    """Старая платежная система (несовместимый интерфейс)"""
    
    def make_payment(self, customer_id, invoice_number, amount):
        print(f"[Legacy] Processing payment for customer {customer_id}, invoice {invoice_number}")
        time.sleep(0.5)  # Имитация обработки
        
        return {
            'success': True,
            'transaction_id': f'TX{customer_id}{invoice_number}',
            'status': 'completed',
            'message': 'Payment processed successfully via legacy system'
        }
    
    def cancel_payment(self, transaction_id):
        print(f"[Legacy] Canceling transaction {transaction_id}")
        return {
            'success': True,
            'message': f'Transaction {transaction_id} canceled'
        }

class NewPaymentSystem(PaymentSystem):
    """Новая платежная система (современный интерфейс)"""
    
    def process(self, amount, details):
        print(f"[New] Processing payment of {amount} with details: {details}")
        time.sleep(0.3)  # Имитация обработки
        
        return {
            'success': True,
            'payment_id': f'PAY-{int(time.time())}',
            'amount': amount,
            'currency': details.get('currency', 'USD'),
            'status': 'success',
            'timestamp': time.time()
        }
    
    def refund(self, transaction_id, amount):
        print(f"[New] Processing refund for {transaction_id}")
        return {
            'success': True,
            'refund_id': f'REF-{transaction_id}',
            'amount': amount,
            'status': 'refunded'
        }

class PayPalSystem:
    """Система PayPal с собственным интерфейсом"""
    
    def send_payment(self, receiver_email, amount, description):
        print(f"[PayPal] Sending {amount} to {receiver_email}")
        return {
            'payment_status': 'COMPLETED',
            'payment_id': f'PAYPAL-{int(time.time())}',
            'amount': {'total': amount, 'currency': 'USD'},
            'description': description
        }

class PaymentAdapter(PaymentSystem):
    """
    Adapter для совместимости различных платежных систем
    с унифицированным интерфейсом
    """
    
    def __init__(self, payment_system):
        self.payment_system = payment_system
    
    def process(self, amount, details):
        """Унифицированный метод обработки платежа"""
        
        if isinstance(self.payment_system, LegacyPaymentSystem):
            # Адаптация для старой системы
            customer_id = details.get('customer_id', '00000')
            invoice_number = details.get('invoice_number', f'INV{int(time.time())}')
            
            result = self.payment_system.make_payment(
                customer_id=customer_id,
                invoice_number=invoice_number,
                amount=amount
            )
            
            # Преобразование результата в унифицированный формат
            return {
                'success': result['success'],
                'payment_id': result['transaction_id'],
                'amount': amount,
                'status': result['status'],
                'message': result['message']
            }
            
        elif isinstance(self.payment_system, NewPaymentSystem):
            # Использование новой системы напрямую
            return self.payment_system.process(amount, details)
            
        elif isinstance(self.payment_system, PayPalSystem):
            # Адаптация для PayPal
            receiver_email = details.get('receiver_email', 'merchant@example.com')
            description = details.get('description', 'E-commerce purchase')
            
            result = self.payment_system.send_payment(
                receiver_email=receiver_email,
                amount=amount,
                description=description
            )
            
            return {
                'success': result['payment_status'] == 'COMPLETED',
                'payment_id': result['payment_id'],
                'amount': result['amount']['total'],
                'currency': result['amount']['currency'],
                'status': 'completed',
                'message': 'PayPal payment processed'
            }
        
        else:
            raise ValueError(f"Unsupported payment system: {type(self.payment_system)}")
    
    def refund(self, transaction_id, amount):
        """Унифицированный метод возврата платежа"""
        
        if isinstance(self.payment_system, LegacyPaymentSystem):
            # У старой системы нет метода refund, используем cancel
            result = self.payment_system.cancel_payment(transaction_id)
            return {
                'success': result['success'],
                'refund_id': f'REF-{transaction_id}',
                'amount': amount,
                'message': result['message']
            }
            
        elif isinstance(self.payment_system, NewPaymentSystem):
            return self.payment_system.refund(transaction_id, amount)
            
        elif isinstance(self.payment_system, PayPalSystem):
            # PayPal требует специальной обработки
            print(f"[PayPal] Processing refund for {transaction_id}")
            return {
                'success': True,
                'refund_id': f'PAYPAL-REF-{transaction_id}',
                'amount': amount,
                'status': 'refunded'
            }
        
        else:
            raise ValueError(f"Unsupported payment system: {type(self.payment_system)}")
    
    def get_system_info(self):
        """Получение информации о платежной системе"""
        system_type = type(self.payment_system).__name__
        
        info = {
            'system': system_type,
            'supported_currencies': ['USD', 'EUR'],
            'requires_authentication': True
        }
        
        if isinstance(self.payment_system, LegacyPaymentSystem):
            info['features'] = ['basic_payments', 'cancellation']
            info['limitations'] = ['no_refunds', 'no_recurring_payments']
        
        elif isinstance(self.payment_system, NewPaymentSystem):
            info['features'] = ['payments', 'refunds', 'recurring', 'subscriptions']
        
        elif isinstance(self.payment_system, PayPalSystem):
            info['features'] = ['payments', 'refunds', 'international']
            info['supported_currencies'] = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
        
        return info

# Пример использования Adapter Pattern
class PaymentProcessor:
    """Класс для демонстрации работы адаптера"""
    
    def __init__(self):
        self.adapters = {}
    
    def register_adapter(self, name, payment_system):
        """Регистрация платежной системы с адаптером"""
        self.adapters[name] = PaymentAdapter(payment_system)
    
    def process_payment(self, adapter_name, amount, details):
        """Обработка платежа через выбранный адаптер"""
        if adapter_name not in self.adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self.adapters[adapter_name]
        return adapter.process(amount, details)
    
    def list_available_systems(self):
        """Список доступных платежных систем"""
        return [
            {
                'name': name,
                'info': adapter.get_system_info()
            }
            for name, adapter in self.adapters.items()
        ]