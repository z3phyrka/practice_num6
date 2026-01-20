from src.controllers.payment_strategy import (
    PaymentContext, 
    CreditCardPayment, 
    PayPalPayment, 
    CryptoPayment
)
import time
from datetime import datetime

class PaymentService:
    """Сервис для обработки платежей"""
    
    def __init__(self):
        self.payment_context = PaymentContext()
    
    def process_payment(self, order_id, amount, payment_method):
        """Обработка платежа"""
        # Выбор стратегии оплаты
        if payment_method == 'credit_card':
            self.payment_context.set_strategy(CreditCardPayment())
        elif payment_method == 'paypal':
            self.payment_context.set_strategy(PayPalPayment())
        elif payment_method == 'crypto':
            self.payment_context.set_strategy(CryptoPayment())
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        # Выполнение оплаты
        try:
            result = self.payment_context.execute_payment(amount)
            
            # Логирование успешного платежа
            self._log_payment(order_id, amount, payment_method, 'success')
            
            return {
                'success': True,
                'message': result,
                'payment_id': f"PAY-{order_id}-{int(time.time())}",
                'order_id': order_id,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            # Логирование ошибки
            self._log_payment(order_id, amount, payment_method, 'failed', str(e))
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def refund_payment(self, payment_id, amount):
        """Возврат платежа"""
        # В реальном приложении здесь была бы интеграция с платежной системой
        print(f"Processing refund for payment {payment_id}: {amount}")
        
        return {
            'success': True,
            'refund_id': f"REF-{payment_id}",
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_payment(self, order_id, amount, method, status, error_message=None):
        """Логирование информации о платеже"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'order_id': order_id,
            'amount': amount,
            'method': method,
            'status': status,
            'error': error_message
        }
        
        # В реальном приложении здесь было бы сохранение в базу данных
        print(f"Payment log: {log_entry}")
        
        return log_entry
    
    def get_payment_methods(self):
        """Получение доступных методов оплаты"""
        return [
            {'id': 'credit_card', 'name': 'Credit Card', 'icon': '💳'},
            {'id': 'paypal', 'name': 'PayPal', 'icon': '🌐'},
            {'id': 'crypto', 'name': 'Cryptocurrency', 'icon': '₿'}
        ]