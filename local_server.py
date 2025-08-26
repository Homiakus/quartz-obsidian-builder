"""
@file: local_server.py
@description: Локальный веб-сервер для предпросмотра Quartz сайта
@dependencies: quartz, http.server
@created: 2024-12-19
"""

import os
import time
import threading
import subprocess
import signal
from pathlib import Path
from typing import Optional, Dict, Any
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

from quartz import run_quartz_build


class QuartzHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Кастомный HTTP обработчик для Quartz сайта"""
    
    def __init__(self, *args, quartz_path: str = None, **kwargs):
        self.quartz_path = Path(quartz_path) if quartz_path else None
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        """Добавляет CORS заголовки для разработки"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Обработка preflight CORS запросов"""
        self.send_response(200)
        self.end_headers()
    
    def translate_path(self, path):
        """Переводит URL путь в файловый путь"""
        if not self.quartz_path:
            return super().translate_path(path)
        
        # Если запрашивается корень, показываем index.html
        if path == '/':
            path = '/index.html'
        
        # Ищем файл в папке public Quartz
        public_path = self.quartz_path / 'public' / path.lstrip('/')
        
        if public_path.exists():
            return str(public_path)
        
        # Fallback к стандартному поведению
        return super().translate_path(path)


class LocalQuartzServer:
    """Локальный сервер для предпросмотра Quartz сайта"""
    
    def __init__(self, quartz_path: str, port: int = 1313):
        self.quartz_path = Path(quartz_path)
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.process: Optional[subprocess.Popen] = None
        
    def start(self):
        """Запускает локальный сервер"""
        if self.is_running:
            return
            
        try:
            # Сначала собираем сайт
            self._build_site()
            
            # Пытаемся запустить через npm (если доступен)
            if self._try_npm_start():
                self.is_running = True
                return
            
            # Fallback к встроенному HTTP серверу
            self._start_http_server()
            
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
            raise
    
    def _build_site(self):
        """Собирает Quartz сайт"""
        try:
            print("🔨 Сборка Quartz сайта...")
            run_quartz_build(str(self.quartz_path))
            print("✅ Сайт собран")
        except Exception as e:
            print(f"⚠️ Ошибка сборки: {e}")
    
    def _try_npm_start(self) -> bool:
        """Пытается запустить через npm start"""
        try:
            package_json = self.quartz_path / 'package.json'
            if not package_json.exists():
                return False
            
            # Проверяем наличие скрипта start
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            if 'scripts' not in package_data or 'start' not in package_data['scripts']:
                return False
            
            # Запускаем npm start
            print("🚀 Запуск через npm start...")
            self.process = subprocess.Popen(
                ['npm', 'start'],
                cwd=str(self.quartz_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Даем время на запуск
            time.sleep(3)
            
            if self.process.poll() is None:
                print(f"✅ Сервер запущен через npm на порту {self.port}")
                return True
            else:
                print("⚠️ npm start завершился с ошибкой")
                return False
                
        except Exception as e:
            print(f"⚠️ npm start недоступен: {e}")
            return False
    
    def _start_http_server(self):
        """Запускает встроенный HTTP сервер"""
        try:
            print("🌐 Запуск встроенного HTTP сервера...")
            
            # Создаем кастомный обработчик
            handler = type('QuartzHandler', (QuartzHTTPRequestHandler,), {
                'quartz_path': str(self.quartz_path)
            })
            
            # Запускаем сервер в отдельном потоке
            self.server = HTTPServer(('localhost', self.port), handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            print(f"✅ HTTP сервер запущен на http://localhost:{self.port}")
            
        except Exception as e:
            print(f"❌ Ошибка запуска HTTP сервера: {e}")
            raise
    
    def stop(self):
        """Останавливает сервер"""
        if not self.is_running:
            return
            
        try:
            # Останавливаем npm процесс
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
            
            # Останавливаем HTTP сервер
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                self.server = None
            
            # Ждем завершения потока
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)
            
            self.is_running = False
            print("✅ Сервер остановлен")
            
        except Exception as e:
            print(f"❌ Ошибка остановки сервера: {e}")
    
    def restart(self):
        """Перезапускает сервер"""
        self.stop()
        time.sleep(1)
        self.start()
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус сервера"""
        return {
            'is_running': self.is_running,
            'port': self.port,
            'quartz_path': str(self.quartz_path),
            'has_npm': self.process is not None,
            'has_http': self.server is not None
        }
    
    def __enter__(self):
        """Контекстный менеджер"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическая остановка при выходе"""
        self.stop()


def create_local_server(quartz_path: str, port: int = 1313) -> LocalQuartzServer:
    """Фабричная функция для создания локального сервера"""
    return LocalQuartzServer(quartz_path, port)
