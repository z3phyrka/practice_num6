import re
from datetime import datetime

class Validators:
    """Класс с методами валидации"""
    
    @staticmethod
    def validate_email(email):
        """Валидация email адреса"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) if email else False
    
    @staticmethod
    def validate_phone(phone):
        """Валидация номера телефона"""
        # Удаление всех нецифровых символов
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10
    
    @staticmethod
    def validate_password(password):
        """Валидация пароля"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_credit_card(card_number, expiry_date, cvv):
        """Валидация данных кредитной карты"""
        # Валидация номера карты (алгоритм Луна)
        digits = [int(d) for d in str(card_number) if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        checksum = 0
        parity = len(digits) % 2
        
        for i, digit in enumerate(digits):
            if i % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        
        if checksum % 10 != 0:
            return False
        
        # Валидация срока действия
        try:
            expiry = datetime.strptime(expiry_date, '%m/%y')
            if expiry < datetime.now():
                return False
        except ValueError:
            return False
        
        # Валидация CVV
        if not (3 <= len(str(cvv)) <= 4) or not str(cvv).isdigit():
            return False
        
        return True
    
    @staticmethod
    def validate_address(address_dict):
        """Валидация адреса"""
        required_fields = ['street', 'city', 'postal_code', 'country']
        
        for field in required_fields:
            if field not in address_dict or not address_dict[field].strip():
                return False, f"Missing field: {field}"
        
        # Валидация почтового индекса (базовая проверка)
        postal_code = address_dict['postal_code']
        if not re.match(r'^[A-Z0-9\s-]{3,10}$', postal_code, re.IGNORECASE):
            return False, "Invalid postal code format"
        
        return True, "Address is valid"