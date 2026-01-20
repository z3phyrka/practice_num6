from abc import ABC, abstractmethod

class Observer(ABC):
    """Абстрактный наблюдатель"""
    
    @abstractmethod
    def update(self, message):
        pass

class Subject:
    """Субъект для наблюдения"""
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer: Observer):
        """Добавить наблюдателя"""
        self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Удалить наблюдателя"""
        self._observers.remove(observer)
    
    def notify(self, message):
        """Уведомить всех наблюдателей"""
        for observer in self._observers:
            observer.update(message)

class EmailNotifier(Observer):
    """Наблюдатель для email уведомлений"""
    
    def update(self, message):
        print(f"Отправка email: {message}")
        # Реальная логика отправки email

class SMSNotifier(Observer):
    """Наблюдатель для SMS уведомлений"""
    
    def update(self, message):
        print(f"Отправка SMS: {message}")
        # Реальная логика отправки SMS

class PushNotifier(Observer):
    """Наблюдатель для push уведомлений"""
    
    def update(self, message):
        print(f"Отправка push уведомления: {message}")
        # Реальная логика отправки push

class OrderNotifier(Subject):
    """Субъект для уведомлений о заказах"""
    
    def order_created(self, order_id):
        self.notify(f"Создан новый заказ #{order_id}")
    
    def order_shipped(self, order_id):
        self.notify(f"Заказ #{order_id} отправлен")