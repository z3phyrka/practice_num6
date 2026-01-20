"""
Facade Pattern - предоставляет упрощенный интерфейс 
к сложной подсистеме электронной коммерции
"""

from src.models import User, Product, Cart, Order
from src.services import ProductService, OrderService, PaymentService
from src.utils import Helpers
from src.views.notifications import OrderNotifier, EmailNotifier
import time

class ECommerceFacade:
    """
    Фасад для системы электронной коммерции.
    Скрывает сложность взаимодействия между различными сервисами
    и предоставляет простые методы для основных операций.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # Инициализация сервисов
        self.product_service = ProductService()
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        
        # Инициализация уведомлений
        self.notifier = OrderNotifier()
        self.notifier.attach(EmailNotifier())
        
        # Кэш для часто используемых данных
        self._cache = {}
    
    def purchase_product(self, user_id, product_id, quantity, payment_method):
        """
        Упрощенный процесс покупки товара.
        Объединяет несколько шагов в один метод.
        """
        print(f"\n{'='*50}")
        print(f"FACADE: Начало процесса покупки")
        print(f"Пользователь: {user_id}, Товар: {product_id}, Количество: {quantity}")
        print(f"{'='*50}\n")
        
        try:
            # 1. Получение пользователя
            user = self._get_user(user_id)
            if not user:
                return self._error_response("Пользователь не найден")
            
            # 2. Получение товара
            product = self._get_product(product_id)
            if not product:
                return self._error_response("Товар не найден")
            
            # 3. Проверка наличия товара
            if not self.product_service.check_availability(product_id, quantity):
                return self._error_response("Недостаточно товара на складе")
            
            # 4. Получение или создание корзины
            cart = self._get_or_create_cart(user_id)
            
            # 5. Добавление товара в корзину
            cart.add_item(product_id, quantity)
            print(f"FACADE: Товар добавлен в корзину")
            
            # 6. Создание заказа из корзины
            order = self._create_order_from_cart(cart, payment_method)
            print(f"FACADE: Создан заказ #{order.id}")
            
            # 7. Обработка оплаты
            payment_result = self._process_payment(order, payment_method)
            if not payment_result['success']:
                return self._error_response(f"Ошибка оплаты: {payment_result.get('error')}")
            
            # 8. Обновление статуса заказа
            order.update_status('paid')
            print(f"FACADE: Статус заказа обновлен на 'paid'")
            
            # 9. Отправка уведомлений
            self._send_notifications(user, order)
            
            # 10. Очистка корзины
            cart.clear()
            
            print(f"\n{'='*50}")
            print(f"FACADE: Покупка успешно завершена!")
            print(f"Заказ: #{order.id}, Оплата: {payment_result['payment_id']}")
            print(f"{'='*50}\n")
            
            return self._success_response({
                'order_id': order.id,
                'order_number': order.order_number,
                'total_amount': order.total_amount,
                'payment_id': payment_result['payment_id'],
                'status': 'completed',
                'message': 'Покупка успешно завершена'
            })
            
        except Exception as e:
            print(f"FACADE: Ошибка в процессе покупки: {str(e)}")
            return self._error_response(f"Внутренняя ошибка системы: {str(e)}")
    
    def get_user_dashboard(self, user_id):
        """
        Получение сводной информации для личного кабинета пользователя.
        Объединяет данные из нескольких источников.
        """
        user = self._get_user(user_id)
        if not user:
            return self._error_response("Пользователь не найден")
        
        # Получение заказов пользователя
        orders = Order.get_by_user(user_id)
        
        # Получение корзины пользователя
        cart = Cart.get_by_user(user_id)
        
        # Получение рекомендаций товаров
        recommendations = self._get_recommendations(user_id)
        
        # Расчет статистики
        stats = self._calculate_user_statistics(user_id, orders)
        
        return self._success_response({
            'user_info': user.to_dict(),
            'orders_summary': {
                'total_orders': len(orders),
                'recent_orders': [order.to_dict() for order in orders[:5]],
                'stats': stats
            },
            'cart_summary': cart.to_dict() if cart else None,
            'recommendations': recommendations,
            'notifications': self._get_user_notifications(user_id)
        })
    
    def search_products_advanced(self, filters):
        """
        Расширенный поиск товаров с фильтрацией.
        Объединяет различные критерии поиска.
        """
        keyword = filters.get('keyword', '')
        category = filters.get('category')
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        sort_by = filters.get('sort_by', 'name')
        
        # Использование сервиса товаров для поиска
        products = self.product_service.search_products(
            keyword=keyword,
            category=category,
            min_price=min_price,
            max_price=max_price
        )
        
        # Сортировка результатов
        sorted_products = self._sort_products(products, sort_by)
        
        # Пагинация
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        paginated = Helpers.paginate(sorted_products, page, per_page)
        
        # Форматирование цен
        for product in paginated['items']:
            product.formatted_price = Helpers.format_price(product.price, 'RUB')
        
        return self._success_response({
            'products': [p.to_dict() for p in paginated['items']],
            'pagination': {
                'page': paginated['page'],
                'per_page': paginated['per_page'],
                'total': paginated['total_items'],
                'pages': paginated['total_pages']
            },
            'filters_applied': filters,
            'search_summary': {
                'keyword': keyword,
                'results_count': paginated['total_items']
            }
        })
    
    def process_return(self, order_id, item_id, reason):
        """
        Обработка возврата товара.
        Координирует работу нескольких сервисов.
        """
        print(f"\nFACADE: Обработка возврата для заказа #{order_id}")
        
        order = Order.get_by_id(order_id)
        if not order:
            return self._error_response("Заказ не найден")
        
        if order.status != 'delivered':
            return self._error_response("Возврат возможен только для доставленных заказов")
        
        # Находим товар в заказе
        return_item = None
        for item in order.items:
            if item.id == item_id:
                return_item = item
                break
        
        if not return_item:
            return self._error_response("Товар не найден в заказе")
        
        # Создание запроса на возврат
        return_request = {
            'order_id': order_id,
            'item_id': item_id,
            'product_id': return_item.product_id,
            'quantity': return_item.quantity,
            'amount': return_item.get_subtotal(),
            'reason': reason,
            'created_at': time.time()
        }
        
        # Обработка возврата платежа
        refund_result = self.payment_service.refund_payment(
            f"ORDER-{order_id}",
            return_request['amount']
        )
        
        if not refund_result['success']:
            return self._error_response("Ошибка при возврате платежа")
        
        # Возврат товара на склад
        product = Product.get_by_id(return_item.product_id)
        if product:
            product.increase_stock(return_item.quantity)
        
        # Обновление статуса заказа
        order.notes = f"Возврат обработан: {reason}"
        order.save()
        
        # Отправка уведомления
        self.notifier.notify(f"Возврат обработан для заказа #{order_id}")
        
        return self._success_response({
            'return_id': refund_result['refund_id'],
            'order_id': order_id,
            'refund_amount': return_request['amount'],
            'status': 'processed',
            'message': 'Возврат успешно обработан'
        })
    
    # ========== Вспомогательные методы ==========
    
    def _get_user(self, user_id):
        """Получение пользователя с кэшированием"""
        cache_key = f"user_{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        user = User.get_by_id(user_id)
        if user:
            self._cache[cache_key] = user
        return user
    
    def _get_product(self, product_id):
        """Получение товара с кэшированием"""
        cache_key = f"product_{product_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        product = self.product_service.get_product_with_details(product_id)
        if product:
            self._cache[cache_key] = product
        return product
    
    def _get_or_create_cart(self, user_id):
        """Получение или создание корзины"""
        cart = Cart.get_by_user(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            cart.save()
        return cart
    
    def _create_order_from_cart(self, cart, payment_method):
        """Создание заказа из корзины"""
        items_data = []
        for item in cart.items:
            items_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': item.product.price
            })
        
        order = self.order_service.create_order(
            user_id=cart.user_id,
            items_data=items_data,
            payment_method=payment_method
        )
        
        return order
    
    def _process_payment(self, order, payment_method):
        """Обработка платежа"""
        return self.payment_service.process_payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method
        )
    
    def _send_notifications(self, user, order):
        """Отправка уведомлений"""
        # Уведомление о создании заказа
        self.notifier.order_created(order.id)
        
        # Email уведомление
        email_body = f"""
        Уважаемый {user.username},
        
        Ваш заказ #{order.id} успешно создан!
        Сумма заказа: {Helpers.format_price(order.total_amount, 'RUB')}
        Статус: {order.status}
        
        Спасибо за покупку!
        """
        
        print(f"FACADE: Отправлено уведомление для заказа #{order.id}")
    
    def _get_recommendations(self, user_id):
        """Получение рекомендаций товаров"""
        # В реальной системе здесь была бы логика рекомендаций
        # Для демонстрации возвращаем популярные товары
        return self.product_service.get_popular_products(limit=5)
    
    def _calculate_user_statistics(self, user_id, orders):
        """Расчет статистики пользователя"""
        if not orders:
            return {
                'total_spent': 0,
                'average_order': 0,
                'favorite_category': None
            }
        
        total_spent = sum(order.total_amount for order in orders)
        average_order = total_spent / len(orders)
        
        return {
            'total_spent': total_spent,
            'average_order': average_order,
            'orders_count': len(orders),
            'last_order_date': max(order.created_at for order in orders).isoformat()
        }
    
    def _sort_products(self, products, sort_by):
        """Сортировка товаров"""
        if sort_by == 'price_asc':
            return sorted(products, key=lambda x: x.price)
        elif sort_by == 'price_desc':
            return sorted(products, key=lambda x: x.price, reverse=True)
        elif sort_by == 'name':
            return sorted(products, key=lambda x: x.name)
        elif sort_by == 'newest':
            return sorted(products, key=lambda x: x.created_at, reverse=True)
        
        return products
    
    def _get_user_notifications(self, user_id):
        """Получение уведомлений пользователя"""
        # В реальной системе здесь была бы логика получения уведомлений
        return [
            {
                'id': 1,
                'type': 'info',
                'message': 'Добро пожаловать в магазин!',
                'read': True,
                'created_at': '2024-01-01T10:00:00'
            }
        ]
    
    def _success_response(self, data):
        """Формирование успешного ответа"""
        return {
            'success': True,
            'data': data,
            'timestamp': time.time()
        }
    
    def _error_response(self, message):
        """Формирование ответа с ошибкой"""
        return {
            'success': False,
            'error': message,
            'timestamp': time.time()
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self._cache.clear()
        print("FACADE: Кэш очищен")

# Пример использования Facade Pattern
def demonstrate_facade_pattern():
    """Демонстрация работы фасада"""
    
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ FACADE PATTERN")
    print("="*60)
    
    # Создание фасада
    facade = ECommerceFacade()
    
    # Пример 1: Покупка товара
    print("\n1. Процесс покупки товара:")
    purchase_result = facade.purchase_product(
        user_id=1,
        product_id=1,
        quantity=2,
        payment_method='credit_card'
    )
    print(f"Результат: {purchase_result}")
    
    # Пример 2: Получение дашборда пользователя
    print("\n2. Дашборд пользователя:")
    dashboard = facade.get_user_dashboard(1)
    if dashboard['success']:
        print(f"Заказов: {dashboard['data']['orders_summary']['total_orders']}")
        print(f"Всего потрачено: {dashboard['data']['orders_summary']['stats']['total_spent']}")
    
    # Пример 3: Поиск товаров
    print("\n3. Расширенный поиск товаров:")
    search_results = facade.search_products_advanced({
        'keyword': 'phone',
        'category': 'electronics',
        'min_price': 100,
        'max_price': 1000,
        'sort_by': 'price_asc'
    })
    print(f"Найдено товаров: {search_results['data']['pagination']['total']}")
    
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*60 + "\n")
    
    return facade