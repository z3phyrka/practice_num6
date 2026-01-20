from datetime import datetime
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Базовый класс для всех моделей"""
    
    def __init__(self, **kwargs):
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @abstractmethod
    def to_dict(self):
        """Преобразование объекта в словарь"""
        pass
    
    @abstractmethod
    def save(self):
        """Сохранение объекта в базу данных"""
        pass
    
    @abstractmethod
    def delete(self):
        """Удаление объекта из базы данных"""
        pass
    
    def update(self, **kwargs):
        """Обновление полей объекта"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    @classmethod
    @abstractmethod
    def get_by_id(cls, id):
        """Получение объекта по ID"""
        pass
    
    @classmethod
    @abstractmethod
    def get_all(cls):
        """Получение всех объектов"""
        pass