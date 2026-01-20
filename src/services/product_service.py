from src.models import Product
from src.views.notifications import Subject, Observer

class ProductService:
    """Сервис для работы с товарами"""
    
    def __init__(self):
        self.notifier = Subject()
    
    def check_availability(self, product_id, quantity):
        """Проверка наличия товара"""
        product = Product.get_by_id(product_id)
        if not product:
            return False
        
        return product.stock >= quantity
    
    def get_product_with_details(self, product_id):
        """Получение товара с детальной информацией"""
        product = Product.get_by_id(product_id)
        if not product:
            return None
        
        # Дополнительная логика (например, получение отзывов, рейтинга и т.д.)
        # В реальном приложении здесь могут быть дополнительные запросы
        
        return product
    
    def update_stock(self, product_id, delta):
        """Обновление количества товара на складе"""
        product = Product.get_by_id(product_id)
        if not product:
            return False
        
        if delta > 0:
            product.increase_stock(delta)
        else:
            success = product.reduce_stock(abs(delta))
            if not success:
                return False
        
        # Уведомление о изменении запасов
        self.notifier.notify(f"Stock updated for product {product_id}: new stock = {product.stock}")
        
        return True
    
    def get_popular_products(self, limit=10):
        """Получение популярных товаров"""
        # В реальном приложении здесь была бы логика расчета популярности
        # Для демонстрации возвращаем случайные товары
        products = Product.get_all()
        return products[:limit] if len(products) > limit else products
    
    def search_products(self, keyword, category=None, min_price=None, max_price=None):
        """Расширенный поиск товаров"""
        query = Product.query
        
        if keyword:
            query = query.filter(
                (Product.name.ilike(f'%{keyword}%')) | 
                (Product.description.ilike(f'%{keyword}%'))
            )
        
        if category:
            query = query.filter_by(category=category)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        return query.all()