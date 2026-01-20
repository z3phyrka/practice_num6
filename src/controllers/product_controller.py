from src.controllers.base_controller import BaseController
from src.models import Product
from src.views import TemplateView

class ProductController(BaseController):
    """Контроллер для управления товарами"""
    
    def __init__(self):
        self.view = TemplateView()
    
    def index(self):
        """Получение списка товаров (GET /products)"""
        products = Product.get_all()
        return self.view.render('product_list.html', products=products)
    
    def show(self, product_id):
        """Получение товара по ID (GET /products/:id)"""
        product = Product.get_by_id(product_id)
        if not product:
            return self.view.error_response('Product not found', 404)
        
        return self.view.render('product_detail.html', product=product)
    
    def create(self):
        """Создание нового товара (POST /products)"""
        data = self.get_request_data()
        
        # Валидация обязательных полей
        required_fields = ['name', 'price', 'category']
        is_valid, error_message = self.validate_required_fields(data, required_fields)
        
        if not is_valid:
            return self.view.error_response(error_message, 400)
        
        # Создание товара
        product = Product.create(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data['category'],
            stock=int(data.get('stock', 0)),
            sku=data.get('sku'),
            image_url=data.get('image_url')
        )
        
        return self.view.render('product_created.html', product=product), 201
    
    def update(self, product_id):
        """Обновление товара (PUT /products/:id)"""
        product = Product.get_by_id(product_id)
        if not product:
            return self.view.error_response('Product not found', 404)
        
        data = self.get_request_data()
        
        # Обновление полей
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'price' in data:
            update_data['price'] = float(data['price'])
        if 'category' in data:
            update_data['category'] = data['category']
        if 'stock' in data:
            update_data['stock'] = int(data['stock'])
        
        product.update(**update_data)
        
        return self.view.render('product_updated.html', product=product)
    
    def delete(self, product_id):
        """Удаление товара (DELETE /products/:id)"""
        product = Product.get_by_id(product_id)
        if not product:
            return self.view.error_response('Product not found', 404)
        
        product.delete()
        return self.view.render('product_deleted.html'), 200
    
    def search(self):
        """Поиск товаров (GET /products/search)"""
        data = self.get_request_data()
        keyword = data.get('q', '')
        
        if not keyword:
            return self.view.error_response('Search keyword is required', 400)
        
        products = Product.search(keyword)
        return self.view.render('product_search.html', products=products, keyword=keyword)
    
    def get_by_category(self, category):
        """Получение товаров по категории (GET /products/category/:category)"""
        products = Product.get_by_category(category)
        return self.view.render('product_category.html', products=products, category=category)