from src.models import Order, Product
from src.views.notifications import OrderNotifier, EmailNotifier, SMSNotifier

class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self):
        self.notifier = OrderNotifier()
        
        # Инициализация наблюдателей
        self.notifier.attach(EmailNotifier())
        self.notifier.attach(SMSNotifier())
    
    def create_order(self, user_id, items_data, shipping_address=None, payment_method=None):
        """Создание нового заказа"""
        # Проверка наличия товаров
        for item in items_data:
            product = Product.get_by_id(item['product_id'])
            if not product or product.stock < item['quantity']:
                raise ValueError(f"Product {item['product_id']} is not available")
        
        # Создание заказа
        order = Order.create(
            user_id=user_id,
            items_data=items_data,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        
        # Уменьшение количества товара на складе
        for item in items_data:
            product = Product.get_by_id(item['product_id'])
            product.reduce_stock(item['quantity'])
        
        # Отправка уведомления
        self.notifier.order_created(order.id)
        
        return order
    
    def update_order_status(self, order_id, new_status):
        """Обновление статуса заказа"""
        order = Order.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.update_status(new_status)
        
        # Отправка уведомления при отправке заказа
        if new_status == 'shipped':
            self.notifier.order_shipped(order.id)
        
        return order
    
    def cancel_order(self, order_id):
        """Отмена заказа"""
        order = Order.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status in ['shipped', 'delivered']:
            raise ValueError("Cannot cancel shipped or delivered order")
        
        # Возврат товара на склад
        for item in order.items:
            product = Product.get_by_id(item.product_id)
            if product:
                product.increase_stock(item.quantity)
        
        order.update_status('cancelled')
        return order
    
    def calculate_order_stats(self, user_id):
        """Расчет статистики заказов пользователя"""
        orders = Order.get_by_user(user_id)
        
        if not orders:
            return {
                'total_orders': 0,
                'total_spent': 0,
                'average_order_value': 0
            }
        
        total_orders = len(orders)
        total_spent = sum(order.total_amount for order in orders)
        average_order_value = total_spent / total_orders
        
        return {
            'total_orders': total_orders,
            'total_spent': total_spent,
            'average_order_value': average_order_value,
            'last_order_date': max(order.created_at for order in orders).isoformat() if orders else None
        }
    
    def notify_user(self, user_id, message):
        """Отправка уведомления пользователю"""
        # В реальном приложении здесь была бы логика отправки уведомлений
        print(f"Notification for user {user_id}: {message}")