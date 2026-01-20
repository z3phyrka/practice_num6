from abc import ABC, abstractmethod
from flask import render_template

class BaseView(ABC):
    """Базовый класс для представлений"""
    
    @abstractmethod
    def render(self, template, **context):
        """Рендеринг шаблона с контекстом"""
        pass
    
    @abstractmethod
    def json_response(self, data, status_code=200):
        """Формирование JSON ответа"""
        pass
    
    @abstractmethod
    def error_response(self, message, status_code=400):
        """Формирование ответа с ошибкой"""
        pass

class TemplateView(BaseView):
    """Представление для работы с шаблонами"""
    
    def __init__(self, template_folder='templates'):
        self.template_folder = template_folder
    
    def render(self, template, **context):
        """Рендеринг HTML шаблона"""
        return render_template(template, **context)
    
    def json_response(self, data, status_code=200):
        """Формирование JSON ответа"""
        from flask import jsonify
        response = jsonify(data)
        response.status_code = status_code
        return response
    
    def error_response(self, message, status_code=400):
        """Формирование ответа с ошибкой"""
        return self.json_response({'error': message}, status_code)
    
    def render_with_layout(self, template, layout='base.html', **context):
        """Рендеринг шаблона с использованием лейаута"""
        context['content_template'] = template
        return self.render(layout, **context)