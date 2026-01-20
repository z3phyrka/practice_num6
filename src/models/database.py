import sqlite3
import threading
from pymongo import MongoClient
from redis import Redis

class DatabaseSingleton:
    """Singleton для управления подключениями к базам данных"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_databases()
        return cls._instance
    
    def _init_databases(self):
        """Инициализация подключений к базам данных"""
        # SQLite для основных данных
        self.sqlite_conn = sqlite3.connect('ecommerce.db', check_same_thread=False)
        
        # MongoDB для товаров
        self.mongo_client = MongoClient('mongodb://localhost:27017/')
        self.mongo_db = self.mongo_client['ecommerce']
        
        # Redis для кэша
        self.redis_client = Redis(host='localhost', port=6379, db=0)
    
    def get_sqlite_connection(self):
        """Получить соединение с SQLite"""
        return self.sqlite_conn
    
    def get_mongo_collection(self, collection_name):
        """Получить коллекцию MongoDB"""
        return self.mongo_db[collection_name]
    
    def get_redis_client(self):
        """Получить клиент Redis"""
        return self.redis_client