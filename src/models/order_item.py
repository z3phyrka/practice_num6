from src import db
from datetime import datetime

class OrderItem(db.Model):
    """Модель позиции заказа"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Цена на момент заказа
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, order_id, product_id, quantity=1, price=0.0):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.get_subtotal(),
            'product': self.product.to_dict() if self.product else None
        }
    
    def save(self):
        """Сохранение позиции заказа"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Удаление позиции заказа"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    def get_subtotal(self):
        """Получение стоимости позиции"""
        return self.price * self.quantity