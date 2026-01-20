from src.controllers.base_controller import BaseController
from src.models import Order, Product, Cart
from src.views import TemplateView
from src.views.notifications import OrderNotifier, EmailNotifier

class OrderController(BaseController):
    """Контроллер для управления заказами"""
    
    def __init__(self):
        self.view = TemplateView()
        self.notifier = OrderNotifier()
        
        # Добавляем наблюдателей
        email_notifier = EmailNotifier()
        self.notifier.attach(email_notifier)
    
    def index(self):
        """Получение списка заказов (GET /orders)"""
        # В реальном приложении здесь была бы аутентификация
        orders = Order.get_by_user(1)  # Демо пользователь
        return self.view.render('order_list.html', orders=orders)
    
    def show(self, order_id):
        """Получение заказа по ID (GET /orders/:id)"""
        order = Order.get_by_id(order_id)
        if not order:
            return self.view.error_response('Order not found', 404)
        
        return self.view.render('order_detail.html', order=order)
    
    def create(self):
        """Создание нового заказа (POST /orders)"""
        data = self.get_request_data()
        
        # Получение корзины пользователя
        cart = Cart.get_by_user(1)  # Демо пользователь
        if not cart or not cart.items:
            return self.view.error_response('Cart is empty', 400)
        
        # Подготовка данных для создания заказа
        items_data = []
        for item in cart.items:
            # Проверка наличия товара
            product = Product.get_by_id(item.product_id)
            if product.stock < item.quantity:
                return self.view.error_response(
                    f'Not enough stock for product: {product.name}',
                    400
                )
            
            items_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': product.price
            })
        
        # Создание заказа
        order = Order.create(
            user_id=1,  # Демо пользователь
            items_data=items_data,
            shipping_address=data.get('shipping_address'),
            payment_method=data.get('payment_method', 'credit_card')
        )
        
        # Уменьшение количества товара на складе
        for item in cart.items:
            product = Product.get_by_id(item.product_id)
            product.reduce_stock(item.quantity)
        
        # Очистка корзины
        cart.clear()
        
        # Отправка уведомлений через Observer
        self.notifier.order_created(order.id)
        
        return self.view.render('order_created.html', order=order), 201
    
    def update(self, order_id):
        """Обновление заказа (PUT /orders/:id)"""
        order = Order.get_by_id(order_id)
        if not order:
            return self.view.error_response('Order not found', 404)
        
        data = self.get_request_data()
        
        # Обновление полей
        if 'status' in data:
            order.status = data['status']
        if 'shipping_address' in data:
            order.shipping_address = data['shipping_address']
        if 'billing_address' in data:
            order.billing_address = data['billing_address']
        if 'payment_method' in data:
            order.payment_method = data['payment_method']
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
        if 'tracking_number' in data:
            order.tracking_number = data['tracking_number']
        if 'notes' in data:
            order.notes = data['notes']
        
        order.save()
        
        # Отправка уведомления об изменении статуса
        if 'status' in data:
            self.notifier.order_shipped(order.id)
        
        return self.view.render('order_updated.html', order=order)
    
    def delete(self, order_id):
        """Удаление заказа (DELETE /orders/:id)"""
        order = Order.get_by_id(order_id)
        if not order:
            return self.view.error_response('Order not found', 404)
        
        # Возврат товара на склад
        for item in order.items:
            product = Product.get_by_id(item.product_id)
            if product:
                product.increase_stock(item.quantity)
        
        order.delete()
        return self.view.render('order_deleted.html'), 200
    
    def process_payment(self, order_id):
        """Обработка оплаты заказа (POST /orders/:id/payment)"""
        order = Order.get_by_id(order_id)
        if not order:
            return self.view.error_response('Order not found', 404)
        
        if order.payment_status == 'paid':
            return self.view.error_response('Order already paid', 400)
        
        # Здесь должна быть логика интеграции с платежной системой
        # Для демонстрации просто отмечаем как оплаченный
        order.mark_as_paid()
        
        return self.view.render('payment_processed.html', order=order), 200