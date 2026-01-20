from flask import render_template, request, jsonify, session
from src.controllers import UserController, ProductController, OrderController, CartController
from src.services.facade.ecommerce_facade import ECommerceFacade
from src.controllers.payment_strategy import PaymentContext, CreditCardPayment, PayPalPayment
from src.api.middleware import authenticate, log_request
from datetime import datetime

def init_routes(app):
    """Инициализация всех маршрутов приложения"""
    
    # Главная страница
    @app.route('/')
    @log_request
    def index():
        return render_template('index.html')
    
    # Страница профиля пользователя
    @app.route('/profile')
    @authenticate
    def user_profile():
        return render_template('user_profile.html')
    
    # ========== CRUD операции для пользователей ==========
    @app.route('/users', methods=['GET'])
    def get_users():
        return UserController.get_users()
    
    @app.route('/users', methods=['POST'])
    def create_user():
        return UserController.create_user()
    
    @app.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        return UserController.get_user(user_id)
    
    @app.route('/users/<int:user_id>', methods=['PUT'])
    @authenticate
    def update_user(user_id):
        return UserController.update_user(user_id)
    
    @app.route('/users/<int:user_id>', methods=['DELETE'])
    @authenticate
    def delete_user(user_id):
        return UserController.delete_user(user_id)
    
    # ========== CRUD операции для товаров ==========
    @app.route('/products', methods=['GET'])
    def get_products():
        controller = ProductController()
        return controller.index()
    
    @app.route('/products/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        controller = ProductController()
        return controller.show(product_id)
    
    @app.route('/products', methods=['POST'])
    @authenticate
    def create_product():
        controller = ProductController()
        return controller.create()
    
    @app.route('/products/<int:product_id>', methods=['PUT'])
    @authenticate
    def update_product(product_id):
        controller = ProductController()
        return controller.update(product_id)
    
    @app.route('/products/<int:product_id>', methods=['DELETE'])
    @authenticate
    def delete_product(product_id):
        controller = ProductController()
        return controller.delete(product_id)
    
    @app.route('/products/search', methods=['GET'])
    def search_products():
        controller = ProductController()
        return controller.search()
    
    @app.route('/products/category/<category>', methods=['GET'])
    def get_products_by_category(category):
        controller = ProductController()
        return controller.get_by_category(category)
    
    # ========== Корзина ==========
    @app.route('/cart', methods=['GET'])
    def view_cart():
        controller = CartController()
        return controller.index()
    
    @app.route('/cart/items', methods=['POST'])
    def add_to_cart():
        controller = CartController()
        return controller.add_item()
    
    @app.route('/cart/items/<int:item_id>', methods=['DELETE'])
    def remove_from_cart(item_id):
        controller = CartController()
        return controller.remove_item(item_id)
    
    @app.route('/cart/<int:cart_id>/clear', methods=['POST'])
    def clear_cart(cart_id):
        controller = CartController()
        return controller.clear_cart(cart_id)
    
    # ========== Заказы ==========
    @app.route('/orders', methods=['GET'])
    @authenticate
    def get_orders():
        controller = OrderController()
        return controller.index()
    
    @app.route('/orders/<int:order_id>', methods=['GET'])
    @authenticate
    def get_order(order_id):
        controller = OrderController()
        return controller.show(order_id)
    
    @app.route('/orders', methods=['POST'])
    @authenticate
    def create_order():
        controller = OrderController()
        return controller.create()
    
    @app.route('/orders/<int:order_id>', methods=['PUT'])
    @authenticate
    def update_order(order_id):
        controller = OrderController()
        return controller.update(order_id)
    
    @app.route('/orders/<int:order_id>', methods=['DELETE'])
    @authenticate
    def delete_order(order_id):
        controller = OrderController()
        return controller.delete(order_id)
    
    @app.route('/orders/<int:order_id>/payment', methods=['POST'])
    @authenticate
    def process_order_payment(order_id):
        controller = OrderController()
        return controller.process_payment(order_id)
    
    # ========== API Gateway маршруты ==========
    @app.route('/api/products', methods=['GET'])
    def api_get_products():
        from src.models import Product
        products = Product.get_all()
        return jsonify([p.to_dict() for p in products])
    
    # Фасад для покупки
    @app.route('/api/purchase', methods=['POST'])
    @authenticate
    def purchase():
        data = request.json
        facade = ECommerceFacade()
        result = facade.purchase_product(
            user_id=data['user_id'],
            product_id=data['product_id'],
            quantity=data['quantity'],
            payment_method=data['payment_method']
        )
        return jsonify(result)
    
    # Стратегия оплаты
    @app.route('/api/payment', methods=['POST'])
    @authenticate
    def process_payment():
        data = request.json
        amount = data['amount']
        method = data['method']
        
        context = PaymentContext()
        
        if method == 'credit_card':
            context.set_strategy(CreditCardPayment())
        elif method == 'paypal':
            context.set_strategy(PayPalPayment())
        else:
            return jsonify({'error': 'Unsupported payment method'}), 400
        
        result = context.execute_payment(amount)
        return jsonify({'message': result, 'timestamp': datetime.now().isoformat()})
    
    # API для адаптеров
    @app.route('/api/shipping/calculate', methods=['POST'])
    def calculate_shipping():
        from src.api.adapters.shipping_adapter import ShippingAdapter, FedExService
        
        data = request.json
        adapter = ShippingAdapter(FedExService())
        result = adapter.calculate_shipping(
            address=data['address'],
            weight=data['weight'],
            dimensions=data['dimensions']
        )
        
        return jsonify(result)
    
    # Health check для микросервисов
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ecommerce-store',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    # Пример маршрута с использованием фабрики
    @app.route('/api/create-user', methods=['POST'])
    def api_create_user():
        from src.factories.model_factory import FactoryProducer
        
        data = request.json
        factory = FactoryProducer.get_factory('user')
        user = factory.create(**data)
        
        # Сохранение в базу данных
        from src import db
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
    
    # Обработка 404 ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'timestamp': datetime.now().isoformat()}), 404
    
    # Обработка 500 ошибок
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'timestamp': datetime.now().isoformat()}), 500