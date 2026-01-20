from src import db
from src.models.base_model import BaseModel
from datetime import datetime

class Product(db.Model, BaseModel):
    """Модель товара"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True)  # Артикул
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __init__(self, name, price, category, stock=0, description="", sku=None, image_url=None):
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock
        self.description = description
        self.sku = sku
        self.image_url = image_url
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock': self.stock,
            'sku': self.sku,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def save(self):
        """Сохранение товара"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Удаление товара"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @classmethod
    def get_by_id(cls, product_id):
        """Получение товара по ID"""
        return cls.query.get(product_id)
    
    @classmethod
    def get_all(cls):
        """Получение всех товаров"""
        return cls.query.all()
    
    @classmethod
    def create(cls, **kwargs):
        """Создание нового товара"""
        product = cls(**kwargs)
        return product.save()
    
    @classmethod
    def get_by_category(cls, category):
        """Получение товаров по категории"""
        return cls.query.filter_by(category=category).all()
    
    @classmethod
    def search(cls, keyword):
        """Поиск товаров по ключевому слову"""
        return cls.query.filter(
            (cls.name.ilike(f'%{keyword}%')) | 
            (cls.description.ilike(f'%{keyword}%'))
        ).all()
    
    def reduce_stock(self, quantity):
        """Уменьшение количества товара на складе"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity):
        """Увеличение количества товара на складе"""
        self.stock += quantity
        self.save()
        return True