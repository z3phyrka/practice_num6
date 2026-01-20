class ShippingAdapter:
    """Адаптер для различных служб доставки"""
    
    def __init__(self, shipping_service):
        self.shipping_service = shipping_service
    
    def calculate_shipping(self, address, weight, dimensions):
        """Расчет стоимости доставки"""
        if hasattr(self.shipping_service, 'get_shipping_cost'):
            # Новая система доставки
            return self.shipping_service.get_shipping_cost(
                destination=address,
                package_weight=weight,
                package_dimensions=dimensions
            )
        elif hasattr(self.shipping_service, 'calculate'):
            # Старая система доставки
            return self.shipping_service.calculate(
                to_address=address,
                weight_kg=weight,
                size=dimensions
            )
        else:
            raise ValueError("Unsupported shipping service")
    
    def create_shipment(self, order_id, address, items):
        """Создание отправления"""
        if hasattr(self.shipping_service, 'create_shipment'):
            return self.shipping_service.create_shipment(
                order_reference=order_id,
                delivery_address=address,
                contents=items
            )
        elif hasattr(self.shipping_service, 'ship'):
            return self.shipping_service.ship(
                order_id=order_id,
                address=address,
                products=items
            )
        else:
            raise ValueError("Unsupported shipment creation")
    
    def track_shipment(self, tracking_number):
        """Отслеживание отправления"""
        if hasattr(self.shipping_service, 'track_package'):
            return self.shipping_service.track_package(tracking_number)
        elif hasattr(self.shipping_service, 'get_status'):
            return self.shipping_service.get_status(tracking_number)
        else:
            raise ValueError("Unsupported tracking method")

# Примеры служб доставки
class FedExService:
    """Служба доставки FedEx"""
    
    def get_shipping_cost(self, destination, package_weight, package_dimensions):
        return {
            'carrier': 'FedEx',
            'cost': 10.99,
            'estimated_days': 3
        }
    
    def create_shipment(self, order_reference, delivery_address, contents):
        return {
            'tracking_number': f"FX{order_reference}",
            'label_url': f"https://fedex.com/labels/{order_reference}"
        }
    
    def track_package(self, tracking_number):
        return {
            'status': 'In transit',
            'location': 'New York',
            'estimated_delivery': '2024-12-25'
        }

class UPSService:
    """Служба доставки UPS"""
    
    def calculate(self, to_address, weight_kg, size):
        return {
            'service': 'UPS Ground',
            'price': 8.99,
            'delivery': '2 business days'
        }
    
    def ship(self, order_id, address, products):
        return {
            'tracking_code': f"UPS{order_id}",
            'shipment_id': f"SH{order_id}"
        }
    
    def get_status(self, tracking_number):
        return {
            'state': 'Delivered',
            'delivered_at': '2024-12-24 14:30:00'
        }