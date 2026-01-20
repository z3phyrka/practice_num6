import time
import functools
from flask import request, jsonify

def timing_decorator(func):
    """Декоратор для измерения времени выполнения функции"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def retry_decorator(max_retries=3, delay=1, exceptions=(Exception,)):
    """Декоратор для повторного выполнения функции при ошибках"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    print(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    time.sleep(delay * (attempt + 1))  # Экспоненциальная задержка
            
            return func(*args, **kwargs)  # Последняя попытка
        return wrapper
    return decorator

def cache_decorator(ttl=300):  # TTL в секундах
    """Декоратор для кэширования результатов функции"""
    cache = {}
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Создание ключа кэша на основе аргументов
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Проверка кэша
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    print(f"Cache hit for {func.__name__}")
                    return cached_data
            
            # Выполнение функции
            result = func(*args, **kwargs)
            
            # Сохранение в кэш
            cache[cache_key] = (result, time.time())
            print(f"Cache miss for {func.__name__}, caching result")
            
            return result
        return wrapper
    return decorator

def validate_request_decorator(required_fields=None, allowed_methods=None):
    """Декоратор для валидации HTTP запросов"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Проверка метода запроса
            if allowed_methods and request.method not in allowed_methods:
                return jsonify({'error': f'Method {request.method} not allowed'}), 405
            
            # Проверка обязательных полей
            if required_fields:
                missing_fields = []
                data = request.get_json() if request.is_json else request.form
                
                for field in required_fields:
                    if field not in data or not str(data[field]).strip():
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'fields': missing_fields
                    }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def role_required_decorator(required_role):
    """Декоратор для проверки роли пользователя"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # В реальном приложении здесь была бы проверка роли из токена или сессии
            # Для демонстрации используем заглушку
            user_role = getattr(request, 'user_role', 'user')
            
            if user_role != required_role and required_role != 'admin':
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_role': required_role,
                    'user_role': user_role
                }), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator