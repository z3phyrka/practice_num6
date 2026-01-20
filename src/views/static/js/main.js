/**
 * Основной JavaScript файл для фронтенда
 * Демонстрация взаимодействия с MVC архитектурой
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('E-commerce store initialized');
    
    // Инициализация компонентов
    initCart();
    initProductFilters();
    initOrderProcessing();
    initNotifications();
    
    // Observer Pattern для отслеживания изменений
    initStateObserver();
});

// ========== Корзина (Cart) ==========

function initCart() {
    const cartButtons = document.querySelectorAll('.add-to-cart-btn');
    const cartCounter = document.getElementById('cart-counter');
    const cartTotal = document.getElementById('cart-total');
    
    // Observer для обновления корзины
    const cartObserver = new CartObserver();
    
    cartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const productPrice = this.dataset.productPrice;
            
            addToCart(productId, productName, productPrice)
                .then(response => {
                    if (response.success) {
                        showNotification('Товар добавлен в корзину!', 'success');
                        
                        // Обновление счетчика корзины
                        updateCartCounter(response.data.itemCount);
                        
                        // Обновление общей суммы
                        if (cartTotal) {
                            cartTotal.textContent = formatPrice(response.data.total);
                        }
                        
                        // Уведомление наблюдателей
                        cartObserver.notify({
                            type: 'cart_updated',
                            data: response.data
                        });
                    } else {
                        showNotification('Ошибка: ' + response.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error adding to cart:', error);
                    showNotification('Ошибка соединения', 'error');
                });
        });
    });
    
    // Функция добавления в корзину
    async function addToCart(productId, productName, productPrice) {
        const response = await fetch('/cart/items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCSRFToken()
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });
        
        return response.json();
    }
    
    // Обновление счетчика корзины
    function updateCartCounter(count) {
        if (cartCounter) {
            cartCounter.textContent = count;
            cartCounter.classList.add('pulse');
            
            setTimeout(() => {
                cartCounter.classList.remove('pulse');
            }, 500);
        }
    }
}

// Observer Pattern для корзины
class CartObserver {
    constructor() {
        this.observers = [];
    }
    
    subscribe(callback) {
        this.observers.push(callback);
    }
    
    unsubscribe(callback) {
        this.observers = this.observers.filter(obs => obs !== callback);
    }
    
    notify(data) {
        this.observers.forEach(observer => observer(data));
    }
}

// ========== Фильтры товаров ==========

function initProductFilters() {
    const searchForm = document.getElementById('search-form');
    const categoryFilter = document.getElementById('category-filter');
    const priceRange = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            performSearch();
        });
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', function() {
            priceValue.textContent = formatPrice(this.value);
        });
        
        priceRange.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    // Strategy Pattern для различных типов фильтрации
    const filterStrategies = {
        'default': filterDefault,
        'category': filterByCategory,
        'price': filterByPrice,
        'search': filterBySearch
    };
    
    async function applyFilters() {
        const filters = {
            category: categoryFilter ? categoryFilter.value : '',
            max_price: priceRange ? priceRange.value : '',
            keyword: document.getElementById('search-input') ? 
                     document.getElementById('search-input').value : ''
        };
        
        // Использование стратегии
        let strategy = 'default';
        if (filters.keyword) strategy = 'search';
        if (filters.category) strategy = 'category';
        if (filters.max_price) strategy = 'price';
        
        const result = await filterStrategies[strategy](filters);
        updateProductList(result);
    }
    
    async function performSearch() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;
        
        const keyword = searchInput.value.trim();
        if (!keyword) return;
        
        try {
            const response = await fetch(`/products/search?q=${encodeURIComponent(keyword)}`);
            const data = await response.json();
            
            updateProductList(data);
            
            // Показать результаты поиска
            document.getElementById('search-results').style.display = 'block';
            document.getElementById('search-query').textContent = keyword;
            
        } catch (error) {
            console.error('Search error:', error);
        }
    }
    
    // Стратегии фильтрации
    async function filterDefault(filters) {
        const response = await fetch('/api/products');
        return response.json();
    }
    
    async function filterByCategory(filters) {
        const response = await fetch(`/products/category/${filters.category}`);
        return response.json();
    }
    
    async function filterByPrice(filters) {
        const response = await fetch(`/api/products?max_price=${filters.max_price}`);
        return response.json();
    }
    
    async function filterBySearch(filters) {
        const response = await fetch(`/products/search?q=${encodeURIComponent(filters.keyword)}`);
        return response.json();
    }
    
    function updateProductList(products) {
        const productGrid = document.querySelector('.products-grid');
        if (!productGrid) return;
        
        if (!Array.isArray(products)) {
            products = products.products || [];
        }
        
        if (products.length === 0) {
            productGrid.innerHTML = '<div class="no-products"><p>Товары не найдены</p></div>';
            return;
        }
        
        let html = '';
        products.forEach(product => {
            html += `
                <div class="product-card">
                    ${product.image_url ? 
                        `<img src="${product.image_url}" alt="${product.name}" class="product-image">` :
                        `<div class="product-image-placeholder">No image</div>`
                    }
                    <div class="product-info">
                        <h3 class="product-name">${product.name}</h3>
                        <p class="product-description">${product.description ? 
                            product.description.substring(0, 100) + 
                            (product.description.length > 100 ? '...' : '') : 
                            ''}</p>
                        <div class="product-details">
                            <span class="product-price">${formatPrice(product.price)}</span>
                            <span class="product-category">${product.category || ''}</span>
                            <span class="product-stock ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}">
                                ${product.stock} в наличии
                            </span>
                        </div>
                        <div class="product-actions">
                            <a href="/products/${product.id}" class="btn btn-info">Подробнее</a>
                            ${product.stock > 0 ? 
                                `<button class="btn btn-primary add-to-cart-btn" 
                                        data-product-id="${product.id}"
                                        data-product-name="${product.name}"
                                        data-product-price="${product.price}">
                                    В корзину
                                </button>` :
                                `<button class="btn btn-disabled" disabled>Нет в наличии</button>`
                            }
                        </div>
                    </div>
                </div>
            `;
        });
        
        productGrid.innerHTML = html;
        
        // Переинициализация кнопок корзины
        initCart();
    }
}

// ========== Обработка заказов ==========

function initOrderProcessing() {
    const checkoutForm = document.getElementById('checkout-form');
    const paymentMethod = document.getElementById('payment-method');
    
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processOrder();
        });
    }
    
    if (paymentMethod) {
        paymentMethod.addEventListener('change', function() {
            updatePaymentDetails(this.value);
        });
    }
    
    // Strategy Pattern для оплаты
    const paymentStrategies = {
        'credit_card': showCreditCardForm,
        'paypal': showPayPalForm,
        'crypto': showCryptoForm
    };
    
    function updatePaymentDetails(method) {
        const paymentDetails = document.getElementById('payment-details');
        if (!paymentDetails) return;
        
        // Скрываем все формы оплаты
        document.querySelectorAll('.payment-form').forEach(form => {
            form.style.display = 'none';
        });
        
        // Показываем нужную форму
        if (paymentStrategies[method]) {
            paymentStrategies[method]();
        }
    }
    
    function showCreditCardForm() {
        const form = document.getElementById('credit-card-form');
        if (form) {
            form.style.display = 'block';
        }
    }
    
    function showPayPalForm() {
        const form = document.getElementById('paypal-form');
        if (form) {
            form.style.display = 'block';
        }
    }
    
    function showCryptoForm() {
        const form = document.getElementById('crypto-form');
        if (form) {
            form.style.display = 'block';
        }
    }
    
    async function processOrder() {
        const checkoutForm = document.getElementById('checkout-form');
        if (!checkoutForm) return;
        
        const formData = new FormData(checkoutForm);
        const orderData = Object.fromEntries(formData.entries());
        
        // Валидация формы
        if (!validateOrderForm(orderData)) {
            return;
        }
        
        // Показываем индикатор загрузки
        showLoading(true);
        
        try {
            // Использование Facade через API
            const response = await fetch('/api/purchase', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': getCSRFToken()
                },
                body: JSON.stringify({
                    user_id: 1, // В реальном приложении из сессии
                    product_id: orderData.product_id,
                    quantity: orderData.quantity || 1,
                    payment_method: orderData.payment_method
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showNotification('Заказ успешно создан!', 'success');
                
                // Перенаправление на страницу заказа
                setTimeout(() => {
                    window.location.href = `/orders/${result.data.order_id}`;
                }, 2000);
                
            } else {
                showNotification('Ошибка: ' + result.error, 'error');
            }
            
        } catch (error) {
            console.error('Order processing error:', error);
            showNotification('Ошибка соединения', 'error');
            
        } finally {
            showLoading(false);
        }
    }
    
    function validateOrderForm(data) {
        if (!data.payment_method) {
            showNotification('Выберите способ оплаты', 'error');
            return false;
        }
        
        // Валидация кредитной карты
        if (data.payment_method === 'credit_card') {
            if (!data.card_number || !data.card_expiry || !data.card_cvv) {
                showNotification('Заполните все поля кредитной карты', 'error');
                return false;
            }
            
            // Простая валидация номера карты
            if (!/^\d{16}$/.test(data.card_number.replace(/\s/g, ''))) {
                showNotification('Неверный номер карты', 'error');
                return false;
            }
        }
        
        return true;
    }
}

// ========== Уведомления (Observer Pattern) ==========

function initNotifications() {
    // Создаем систему уведомлений
    const notificationSystem = new NotificationSystem();
    
    // Подписываемся на события
    notificationSystem.subscribe('cart_updated', function(data) {
        console.log('Cart updated notification:', data);
        
        // Можно обновлять UI или показывать toast-уведомления
        if (data.type === 'item_added') {
            showToast('Товар добавлен в корзину');
        }
    });
    
    notificationSystem.subscribe('order_created', function(data) {
        console.log('Order created notification:', data);
        showToast('Заказ успешно создан!');
    });
    
    // Пример отправки уведомления
    setTimeout(() => {
        notificationSystem.notify('order_created', { orderId: 123, status: 'pending' });
    }, 5000);
}

class NotificationSystem {
    constructor() {
        this.subscribers = {};
    }
    
    subscribe(event, callback) {
        if (!this.subscribers[event]) {
            this.subscribers[event] = [];
        }
        this.subscribers[event].push(callback);
    }
    
    unsubscribe(event, callback) {
        if (this.subscribers[event]) {
            this.subscribers[event] = this.subscribers[event].filter(
                cb => cb !== callback
            );
        }
    }
    
    notify(event, data) {
        if (this.subscribers[event]) {
            this.subscribers[event].forEach(callback => {
                callback(data);
            });
        }
    }
}

// ========== Наблюдатель за состоянием (State Observer) ==========

function initStateObserver() {
    // Observer для отслеживания изменений состояния приложения
    const state = {
        cart: [],
        user: null,
        products: []
    };
    
    const stateObserver = new Proxy(state, {
        set(target, property, value) {
            console.log(`State changed: ${property} =`, value);
            
            // Вызываем обработчики изменений
            if (property === 'cart') {
                updateCartUI(value);
            }
            
            // Продолжаем обычное поведение
            target[property] = value;
            return true;
        }
    });
    
    // Инициализация начального состояния
    fetchInitialState(stateObserver);
}

async function fetchInitialState(stateObserver) {
    try {
        // Загрузка данных корзины
        const cartResponse = await fetch('/api/cart');
        if (cartResponse.ok) {
            stateObserver.cart = await cartResponse.json();
        }
        
        // Загрузка данных пользователя
        const userResponse = await fetch('/api/user/profile');
        if (userResponse.ok) {
            stateObserver.user = await userResponse.json();
        }
        
        // Загрузка товаров
        const productsResponse = await fetch('/api/products');
        if (productsResponse.ok) {
            stateObserver.products = await productsResponse.json();
        }
        
    } catch (error) {
        console.error('Error fetching initial state:', error);
    }
}

function updateCartUI(cartData) {
    // Обновление UI на основе состояния корзины
    const cartCounter = document.getElementById('cart-counter');
    if (cartCounter && cartData.items) {
        const itemCount = cartData.items.reduce((sum, item) => sum + item.quantity, 0);
        cartCounter.textContent = itemCount;
    }
}

// ========== Вспомогательные функции ==========

function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Добавляем в документ
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Закрытие по кнопке
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Автоматическое закрытие
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

function showLoading(show) {
    let loader = document.getElementById('global-loader');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.className = 'loader-overlay';
            loader.innerHTML = '<div class="loader"></div>';
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    } else {
        if (loader) {
            loader.style.display = 'none';
        }
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(price);
}

function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
}

// Добавляем CSS для уведомлений и загрузчика
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        padding: 1rem;
        max-width: 300px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 1000;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #28a745;
    }
    
    .notification-error {
        border-left: 4px solid #dc3545;
    }
    
    .notification-info {
        border-left: 4px solid #17a2b8;
    }
    
    .notification-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: #666;
    }
    
    .toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(100%);
        background: #333;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        transition: transform 0.3s ease;
        z-index: 1000;
    }
    
    .toast.show {
        transform: translateX(-50%) translateY(0);
    }
    
    .loader-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255,255,255,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loader {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .pulse {
        animation: pulse 0.5s ease;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .payment-form {
        display: none;
        margin-top: 1rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 4px;
    }
`;
document.head.appendChild(style);