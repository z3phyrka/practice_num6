import requests
from flask import request, jsonify
from src.services.facade import ECommerceFacade

class APIGateway:
    """API Gateway для маршрутизации запросов к микросервисам"""
    
    def __init__(self, config):
        self.config = config
        self.facade = ECommerceFacade()
        
        # URL микросервисов
        self.product_service_url = config.get('PRODUCT_SERVICE_URL')
        self.order_service_url = config.get('ORDER_SERVICE_URL')
        self.payment_service_url = config.get('PAYMENT_SERVICE_URL')
    
    def route_request(self, service_name, endpoint, method='GET', data=None):
        """Маршрутизация запроса к микросервису"""
        # Определение URL целевого сервиса
        if service_name == 'products':
            base_url = self.product_service_url
        elif service_name == 'orders':
            base_url = self.order_service_url
        elif service_name == 'payments':
            base_url = self.payment_service_url
        else:
            return {'error': f'Unknown service: {service_name}'}, 400
        
        # Формирование полного URL
        url = f"{base_url}{endpoint}"
        
        try:
            # Отправка запроса к микросервису
            if method == 'GET':
                response = requests.get(url, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                return {'error': f'Unsupported method: {method}'}, 400
            
            # Возврат ответа от микросервиса
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Service unavailable: {str(e)}'}, 503
    
    def handle_product_request(self):
        """Обработка запроса к сервису товаров через Facade"""
        endpoint = request.path.replace('/api/products', '')
        return self.route_request('products', endpoint, request.method, request.json)
    
    def handle_order_request(self):
        """Обработка запроса к сервису заказов через Facade"""
        endpoint = request.path.replace('/api/orders', '')
        
        # Для создания заказа используем Facade
        if request.method == 'POST' and endpoint == '/':
            data = request.json
            try:
                result = self.facade.purchase_product(
                    user_id=data.get('user_id'),
                    product_id=data.get('product_id'),
                    quantity=data.get('quantity', 1),
                    payment_method=data.get('payment_method', 'credit_card')
                )
                return jsonify(result), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        return self.route_request('orders', endpoint, request.method, request.json)
    
    def handle_payment_request(self):
        """Обработка запроса к сервису платежей"""
        endpoint = request.path.replace('/api/payments', '')
        return self.route_request('payments', endpoint, request.method, request.json)
    
    def get_aggregated_data(self, user_id):
        """Получение агрегированных данных пользователя"""
        # Сбор данных из нескольких сервисов
        aggregated_data = {
            'user_id': user_id,
            'services': []
        }
        
        # Получение данных о заказах
        try:
            orders_response = requests.get(f"{self.order_service_url}/users/{user_id}/orders")
            if orders_response.status_code == 200:
                aggregated_data['orders'] = orders_response.json()
                aggregated_data['services'].append('orders')
        except:
            pass
        
        # Получение данных о корзине
        try:
            cart_response = requests.get(f"{self.order_service_url}/users/{user_id}/cart")
            if cart_response.status_code == 200:
                aggregated_data['cart'] = cart_response.json()
                aggregated_data['services'].append('cart')
        except:
            pass
        
        return aggregated_data