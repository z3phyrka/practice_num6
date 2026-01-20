from src.controllers.base_controller import BaseController
from src.models import Cart, Product, CartItem
from src.views import TemplateView
from src import db  # Импортируем db из основного модуля

class CartController(BaseController):
    """Контроллер для управления корзиной"""
    
    def __init__(self):
        self.view = TemplateView()
    
    def index(self):
        """Получение корзины (GET /cart)"""
        # В реальном приложении здесь была бы аутентификация
        cart = self._get_or_create_cart()
        return self.view.render('cart.html', cart=cart)
    
    def show(self, cart_id):
        """Получение корзины по ID (GET /cart/:id)"""
        cart = Cart.get_by_id(cart_id)
        if not cart:
            return self.view.error_response('Cart not found', 404)
        
        return self.view.render('cart_detail.html', cart=cart)
    
    def create(self):
        """Создание новой корзины (POST /cart)"""
        data = self.get_request_data()
        
        cart = Cart(
            user_id=data.get('user_id'),
            session_id=data.get('session_id')
        )
        cart.save()
        
        return self.view.render('cart_created.html', cart=cart), 201
    
    def update(self, cart_id):
        """Обновление корзины (PUT /cart/:id)"""
        cart = Cart.get_by_id(cart_id)
        if not cart:
            return self.view.error_response('Cart not found', 404)
        
        data = self.get_request_data()
        
        if 'user_id' in data:
            cart.user_id = data['user_id']
        if 'session_id' in data:
            cart.session_id = data['session_id']
        
        cart.save()
        return self.view.render('cart_updated.html', cart=cart)
    
    def delete(self, cart_id):
        """Удаление корзины (DELETE /cart/:id)"""
        cart = Cart.get_by_id(cart_id)
        if not cart:
            return self.view.error_response('Cart not found', 404)
        
        cart.delete()
        return self.view.render('cart_deleted.html'), 200
    
    def add_item(self):
        """Добавление товара в корзину (POST /cart/items)"""
        data = self.get_request_data()
        
        required_fields = ['product_id']
        is_valid, error_message = self.validate_required_fields(data, required_fields)
        
        if not is_valid:
            return self.view.error_response(error_message, 400)
        
        cart = self._get_or_create_cart()
        product_id = int(data['product_id'])
        quantity = int(data.get('quantity', 1))
        
        # Проверка существования товара
        product = Product.get_by_id(product_id)
        if not product:
            return self.view.error_response('Product not found', 404)
        
        # Проверка наличия товара на складе
        if product.stock < quantity:
            return self.view.error_response('Not enough stock', 400)
        
        cart.add_item(product_id, quantity)
        
        return self.view.render('item_added.html', cart=cart, product=product), 200
    
    def remove_item(self, item_id):
        """Удаление товара из корзины (DELETE /cart/items/:id)"""
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return self.view.error_response('Cart item not found', 404)
        
        db.session.delete(cart_item)
        db.session.commit()
        
        cart = Cart.get_by_id(cart_item.cart_id)
        return self.view.render('item_removed.html', cart=cart), 200
    
    def clear_cart(self, cart_id):
        """Очистка корзины (POST /cart/:id/clear)"""
        cart = Cart.get_by_id(cart_id)
        if not cart:
            return self.view.error_response('Cart not found', 404)
        
        cart.clear()
        return self.view.render('cart_cleared.html', cart=cart), 200
    
    def _get_or_create_cart(self):
        """Получение или создание корзины для текущего пользователя/сессии"""
        # В реальном приложении здесь была бы логика аутентификации
        # Для демонстрации используем фиксированный user_id
        cart = Cart.get_by_user(1)  # Демо пользователь
        
        if not cart:
            cart = Cart(user_id=1)
            cart.save()
        
        return cart