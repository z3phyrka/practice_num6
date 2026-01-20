"""
API Gateway и модули для микросервисной архитектуры
"""

from src.api.gateway import APIGateway
from src.api.routes import init_routes
from src.api.middleware import (
    rate_limit,
    authenticate,
    log_request,
    validate_json
)
from src.api.adapters.payment_adapter import (
    LegacyPaymentSystem,
    NewPaymentSystem,
    PaymentAdapter
)
from src.api.adapters.shipping_adapter import (
    ShippingAdapter,
    FedExService,
    UPSService
)

__all__ = [
    'APIGateway',
    'init_routes',
    'rate_limit',
    'authenticate',
    'log_request',
    'validate_json',
    'LegacyPaymentSystem',
    'NewPaymentSystem',
    'PaymentAdapter',
    'ShippingAdapter',
    'FedExService',
    'UPSService'
]