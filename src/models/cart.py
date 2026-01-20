from src import db
from src.models.base_model import BaseModel
from datetime import datetime

class Cart(db.Model, BaseModel):
    """Модель корзины покупателя"""
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    session_id = db.Column(db.String(100))  # Для неавторизованных пользователей
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id=None, session_id=None):
        self.user_id = user_id
        self.session_id = session_id
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items],
            'total': self.get_total()
        }
    
    def save(self):
        """Сохранение корзины"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Удаление корзины"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @classmethod
    def get_by_id(cls, cart_id):
        """Получение корзины по ID"""
        return cls.query.get(cart_id)
    
    @classmethod
    def get_all(cls):
        """Получение всех корзин"""
        return cls.query.all()
    
    @classmethod
    def get_by_user(cls, user_id):
        """Получение корзины пользователя"""
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def get_by_session(cls, session_id):
        """Получение корзины по сессии"""
        return cls.query.filter_by(session_id=session_id).first()
    
    def add_item(self, product_id, quantity=1):
        """Добавление товара в корзину"""
        from src.models.cart_item import CartItem
        
        # Проверка, есть ли уже такой товар в корзине
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            cart_item = CartItem(
                cart_id=self.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return self
    
    def remove_item(self, product_id):
        """Удаление товара из корзины"""
        from src.models.cart_item import CartItem
        
        cart_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
        
        return self
    
    def update_item_quantity(self, product_id, quantity):
        """Обновление количества товара в корзине"""
        from src.models.cart_item import CartItem
        
        cart_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()
        
        if cart_item:
            if quantity <= 0:
                db.session.delete(cart_item)
            else:
                cart_item.quantity = quantity
                cart_item.save()
            
            db.session.commit()
        
        return self
    
    def clear(self):
        """Очистка корзины"""
        from src.models.cart_item import CartItem
        
        CartItem.query.filter_by(cart_id=self.id).delete()
        db.session.commit()
        return self
    
    def get_total(self):
        """Получение общей стоимости корзины"""
        total = 0
        for item in self.items:
            total += item.get_subtotal()
        return total
    
    def get_item_count(self):
        """Получение количества товаров в корзине"""
        return sum(item.quantity for item in self.items)