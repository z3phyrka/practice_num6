import threading
import queue
import time
import random

class Producer:
    """Производитель задач"""
    
    def __init__(self, task_queue):
        self.task_queue = task_queue
        self.running = True
    
    def generate_task(self):
        """Генерация задачи"""
        task_types = ['process_order', 'send_email', 'update_inventory', 'generate_report']
        task_type = random.choice(task_types)
        task_data = {
            'type': task_type,
            'id': random.randint(1000, 9999),
            'timestamp': time.time()
        }
        return task_data
    
    def run(self):
        """Основной цикл производителя"""
        while self.running:
            task = self.generate_task()
            self.task_queue.put(task)
            print(f"Producer: создана задача {task['type']} #{task['id']}")
            time.sleep(random.uniform(0.5, 2.0))

class Consumer:
    """Потребитель задач"""
    
    def __init__(self, task_queue, result_queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
    
    def process_task(self, task):
        """Обработка задачи"""
        time.sleep(random.uniform(0.1, 1.0))  # Имитация обработки
        
        result = {
            'task_id': task['id'],
            'status': 'completed',
            'processed_at': time.time(),
            'message': f"Задача {task['type']} #{task['id']} обработана"
        }
        
        return result
    
    def run(self):
        """Основной цикл потребителя"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                result = self.process_task(task)
                self.result_queue.put(result)
                print(f"Consumer: {result['message']}")
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue