import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.models import User
from src.views.notifications import Observer

class NotificationService(Observer):
    """Сервис для отправки уведомлений"""
    
    def __init__(self, config):
        self.config = config
        self.smtp_server = config.get('MAIL_SERVER')
        self.smtp_port = config.get('MAIL_PORT')
        self.smtp_username = config.get('MAIL_USERNAME')
        self.smtp_password = config.get('MAIL_PASSWORD')
    
    def update(self, message):
        """Обработка уведомления от Subject"""
        print(f"Notification received: {message}")
        # В реальном приложении здесь была бы логика отправки уведомлений
    
    def send_email(self, to_email, subject, body, html_body=None):
        """Отправка email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Текстовое содержимое
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # HTML содержимое (если есть)
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Подключение к SMTP серверу
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_order_confirmation(self, order_id, user_id):
        """Отправка подтверждения заказа"""
        user = User.get_by_id(user_id)
        if not user:
            return False
        
        subject = f"Order Confirmation #{order_id}"
        body = f"Hello {user.username},\n\nYour order #{order_id} has been confirmed.\n\nThank you for your purchase!"
        
        html_body = f"""
        <html>
            <body>
                <h1>Order Confirmation</h1>
                <p>Hello {user.username},</p>
                <p>Your order <strong>#{order_id}</strong> has been confirmed.</p>
                <p>Thank you for your purchase!</p>
            </body>
        </html>
        """
        
        return self.send_email(user.email, subject, body, html_body)
    
    def send_password_reset(self, user_id, reset_token):
        """Отправка ссылки для сброса пароля"""
        user = User.get_by_id(user_id)
        if not user:
            return False
        
        reset_link = f"https://example.com/reset-password?token={reset_token}"
        
        subject = "Password Reset Request"
        body = f"Hello {user.username},\n\nTo reset your password, click the link below:\n{reset_link}\n\nThis link will expire in 1 hour."
        
        html_body = f"""
        <html>
            <body>
                <h1>Password Reset</h1>
                <p>Hello {user.username},</p>
                <p>To reset your password, click the link below:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
            </body>
        </html>
        """
        
        return self.send_email(user.email, subject, body, html_body)