from src import db
from src.models.base_model import BaseModel
from datetime import datetime
import uuid

class Order(db.Model, BaseModel):
    """Модель заказа"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, paid, shipped, delivered, cancelled
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='unpaid')
    tracking_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, total_amount, shipping_address=None, 
                 billing_address=None, payment_method=None, notes=None):
        self.order_number = self._generate_order_number()
        self.user_id = user_id
        self.total_amount = total_amount
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.payment_method = payment_method
        self.notes = notes
    
    def _generate_order_number(self):
        """Генерация уникального номера заказа"""
        return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4().hex[:8]).upper()}"
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'tracking_number': self.tracking_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    def save(self):
        """Сохранение заказа"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Удаление заказа"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @classmethod
    def get_by_id(cls, order_id):
        """Получение заказа по ID"""
        return cls.query.get(order_id)
    
    @classmethod
    def get_all(cls):
        """Получение всех заказов"""
        return cls.query.all()
    
    @classmethod
    def get_by_user(cls, user_id):
        """Получение заказов пользователя"""
        return cls.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def create(cls, user_id, items_data, shipping_address=None, payment_method=None):
        """Создание нового заказа"""
        from src.models.order_item import OrderItem
        
        # Расчет общей суммы
        total_amount = sum(item['price'] * item['quantity'] for item in items_data)
        
        order = cls(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        
        order.save()
        
        # Создание позиций заказа
        for item_data in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        return order
    
    def update_status(self, new_status):
        """Обновление статуса заказа"""
        self.status = new_status
        self.save()
        return self
    
    def mark_as_paid(self):
        """Отметить заказ как оплаченный"""
        self.payment_status = 'paid'
        self.status = 'paid'
        self.save()
        return self