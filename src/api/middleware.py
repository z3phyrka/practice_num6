import time
from functools import wraps
from flask import request, jsonify
import json

def rate_limit(max_requests, window_size):
    """Middleware для ограничения скорости запросов"""
    requests = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            # Очистка старых записей
            requests[ip] = [t for t in requests.get(ip, []) 
                           if current_time - t < window_size]
            
            # Проверка количества запросов
            if len(requests[ip]) >= max_requests:
                return jsonify({
                    'error': 'Too many requests',
                    'retry_after': window_size,
                    'timestamp': time.time()
                }), 429
            
            # Добавление текущего запроса
            requests[ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authenticate(f):
    """Middleware для аутентификации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # В реальном приложении здесь была бы проверка токена
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required', 'timestamp': time.time()}), 401
        
        # Для демонстрации принимаем любой токен
        token = auth_header.split(' ')[1]
        
        # В реальном приложении здесь была бы валидация токена
        if not token:
            return jsonify({'error': 'Invalid token', 'timestamp': time.time()}), 401
        
        # Добавление информации о пользователе в request
        request.user_id = 1  # Демо пользователь
        
        return f(*args, **kwargs)
    return decorated_function

def log_request(f):
    """Middleware для логирования запросов"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Выполнение запроса
        response = f(*args, **kwargs)
        
        # Логирование информации
        log_data = {
            'timestamp': time.time(),
            'method': request.method,
            'endpoint': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else 'Unknown',
            'response_time': time.time() - start_time,
            'status_code': response[1] if isinstance(response, tuple) else 200
        }
        
        print(f"Request log: {log_data}")
        
        return response
    return decorated_function

def validate_json(required_fields=None):
    """Middleware для валидации JSON (упрощенная версия без jsonschema)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json', 'timestamp': time.time()}), 400
            
            try:
                data = request.get_json()
                
                # Проверка обязательных полей
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        return jsonify({
                            'error': 'Missing required fields',
                            'fields': missing_fields,
                            'timestamp': time.time()
                        }), 400
                
                request.validated_data = data
            except Exception as e:
                return jsonify({'error': 'Invalid JSON data', 'details': str(e), 'timestamp': time.time()}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cors_headers(f):
    """Middleware для добавления CORS заголовков"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if isinstance(response, tuple):
            # Если ответ кортеж (data, status)
            data, status = response
            response_obj = jsonify(data)
            response_obj.status_code = status
        else:
            response_obj = response
        
        # Добавляем CORS заголовки
        response_obj.headers.add('Access-Control-Allow-Origin', '*')
        response_obj.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response_obj.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response_obj
    return decorated_function