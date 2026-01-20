from abc import ABC, abstractmethod
from flask import request, jsonify

class BaseController(ABC):
    """Базовый класс для контроллеров"""
    
    @abstractmethod
    def index(self):
        """Получение списка объектов"""
        pass
    
    @abstractmethod
    def show(self, id):
        """Получение объекта по ID"""
        pass
    
    @abstractmethod
    def create(self):
        """Создание нового объекта"""
        pass
    
    @abstractmethod
    def update(self, id):
        """Обновление объекта"""
        pass
    
    @abstractmethod
    def delete(self, id):
        """Удаление объекта"""
        pass
    
    def get_request_data(self):
        """Получение данных из запроса"""
        if request.is_json:
            return request.get_json()
        elif request.form:
            return request.form.to_dict()
        elif request.args:
            return request.args.to_dict()
        return {}
    
    def validate_required_fields(self, data, required_fields):
        """Валидация обязательных полей"""
        missing_fields = []
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    def success_response(self, data=None, message="Success", status_code=200):
        """Формирование успешного ответа"""
        response_data = {'success': True, 'message': message}
        if data is not None:
            response_data['data'] = data
        
        response = jsonify(response_data)
        response.status_code = status_code
        return response
    
    def error_response(self, message="Error", status_code=400):
        """Формирование ответа с ошибкой"""
        response = jsonify({'success': False, 'error': message})
        response.status_code = status_code
        return response