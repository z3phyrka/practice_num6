from src import db
from datetime import datetime

class CartItem(db.Model):
    """Модель позиции корзины"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, cart_id, product_id, quantity=1):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'product': self.product.to_dict() if self.product else None,
            'subtotal': self.get_subtotal()
        }
    
    def save(self):
        """Сохранение позиции корзины"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Удаление позиции корзины"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    def get_subtotal(self):
        """Получение стоимости позиции"""
        if self.product:
            return self.product.price * self.quantity
        return 0