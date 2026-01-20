from flask import request, jsonify, render_template
from src.models import User
from src import db

class UserController:
    """Контроллер для управления пользователями"""
    
    @staticmethod
    def get_users():
        """Получить всех пользователей (GET /users)"""
        users = User.get_all()
        return render_template('user_list.html', users=users)
    
    @staticmethod
    def get_user(user_id):
        """Получить пользователя по ID (GET /users/:id)"""
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return render_template('user_detail.html', user=user)
    
    @staticmethod
    def create_user():
        """Создать нового пользователя (POST /users)"""
        data = request.form
        if not data.get('username') or not data.get('email'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # В реальном приложении здесь должно быть хеширование пароля
        user = User.create(
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password', '')
        )
        
        return render_template('user_created.html', user=user), 201
    
    @staticmethod
    def update_user(user_id):
        """Обновить пользователя (PUT /users/:id)"""
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.form
        user.update(**data)
        return render_template('user_updated.html', user=user)
    
    @staticmethod
    def delete_user(user_id):
        """Удалить пользователя (DELETE /users/:id)"""
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.delete()
        return render_template('user_deleted.html'), 200