"""
@file: auto_launcher.py
@description: Автоматический запуск сайта при изменениях в базе знаний
@dependencies: deployment_manager, local_server
@created: 2024-12-19
"""

import os
import time
import threading
from pathlib import Path
from typing import Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from local_server import LocalQuartzServer


class KnowledgeBaseWatcher(FileSystemEventHandler):
    """Отслеживает изменения в базе знаний и автоматически запускает сайт"""
    
    def __init__(self, vault_path: str, callback: Optional[Callable] = None):
        self.vault_path = Path(vault_path)
        self.callback = callback
        self.last_modified = time.time()
        self.debounce_time = 2.0  # Задержка в секундах для избежания множественных запусков
        self.is_running = False
        
    def on_modified(self, event):
        """Обработчик изменения файлов"""
        if event.is_directory:
            return
            
        # Проверяем что файл находится в базе знаний
        if not str(event.src_path).startswith(str(self.vault_path)):
            return
            
        # Проверяем расширение файла (только markdown и связанные)
        if not event.src_path.endswith(('.md', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
            return
            
        current_time = time.time()
        if current_time - self.last_modified > self.debounce_time:
            self.last_modified = current_time
            self._trigger_site_update()
    
    def on_created(self, event):
        """Обработчик создания новых файлов"""
        if event.is_directory:
            return
        self._trigger_site_update()
    
    def on_deleted(self, event):
        """Обработчик удаления файлов"""
        if event.is_directory:
            return
        self._trigger_site_update()
    
    def _trigger_site_update(self):
        """Запускает обновление сайта"""
        if self.is_running:
            return
            
        self.is_running = True
        threading.Thread(target=self._update_site, daemon=True).start()
    
    def _update_site(self):
        """Обновляет сайт в фоновом режиме"""
        try:
            if self.callback:
                self.callback()
        finally:
            self.is_running = False


class AutoLauncher:
    """Основной класс автоматического запуска"""
    
    def __init__(self, vault_path: str, quartz_path: str):
        self.vault_path = Path(vault_path)
        self.quartz_path = Path(quartz_path)
        self.observer = None
        self.watcher = None
        self.local_server = None
        self.is_watching = False
        
    def start_watching(self, callback: Optional[Callable] = None):
        """Начинает отслеживание изменений"""
        if self.is_watching:
            return
            
        try:
            # Создаем наблюдатель
            self.watcher = KnowledgeBaseWatcher(str(self.vault_path), callback)
            self.observer = Observer()
            self.observer.schedule(self.watcher, str(self.vault_path), recursive=True)
            self.observer.start()
            
            self.is_watching = True
            print(f"✅ Отслеживание изменений запущено для: {self.vault_path}")
            
        except Exception as e:
            print(f"❌ Ошибка запуска отслеживания: {e}")
    
    def stop_watching(self):
        """Останавливает отслеживание изменений"""
        if not self.is_watching:
            return
            
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            self.is_watching = False
            print("✅ Отслеживание изменений остановлено")
            
        except Exception as e:
            print(f"❌ Ошибка остановки отслеживания: {e}")
    
    def launch_local_site(self, port: int = 1313):
        """Запускает локальный сайт для предпросмотра"""
        try:
            if not self.local_server:
                self.local_server = LocalQuartzServer(str(self.quartz_path), port)
            
            self.local_server.start()
            print(f"🌐 Локальный сайт запущен на http://localhost:{port}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска локального сайта: {e}")
            return False
    
    def stop_local_site(self):
        """Останавливает локальный сайт"""
        try:
            if self.local_server:
                self.local_server.stop()
                self.local_server = None
                print("✅ Локальный сайт остановлен")
                
        except Exception as e:
            print(f"❌ Ошибка остановки локального сайта: {e}")
    
    def rebuild_and_restart(self):
        """Пересобирает сайт и перезапускает сервер"""
        try:
            print("🔄 Пересборка сайта...")
            
            # Останавливаем текущий сервер
            if self.local_server:
                self.local_server.stop()
            
            # Пересобираем Quartz
            from quartz import run_quartz_build
            run_quartz_build(str(self.quartz_path))
            
            # Запускаем заново
            self.launch_local_site()
            
            print("✅ Сайт пересобран и перезапущен")
            
        except Exception as e:
            print(f"❌ Ошибка пересборки: {e}")
    
    def __enter__(self):
        """Контекстный менеджер"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическая очистка при выходе"""
        self.stop_watching()
        self.stop_local_site()


def create_auto_launcher(vault_path: str, quartz_path: str) -> AutoLauncher:
    """Фабричная функция для создания AutoLauncher"""
    return AutoLauncher(vault_path, quartz_path)
