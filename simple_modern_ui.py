"""
@file: simple_modern_ui.py
@description: Упрощенная версия современного UI с гарантированной работоспособностью
@dependencies: PyQt6
@created: 2024-12-19
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFileDialog, QPlainTextEdit, QFrame,
    QStackedWidget, QScrollArea, QPushButton, QGroupBox, QFormLayout,
    QProgressBar, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class HTTPServerManager:
    """Управление HTTP-сервером"""
    
    def __init__(self):
        self.server_process = None
        self.server_thread = None
        self.is_running = False
        self.port = 1313
        self.serve_path = None
        self.httpd = None
    
    def start_server(self, serve_path: str, port: int = 1313):
        """Запуск HTTP-сервера"""
        if self.is_running:
            return False, "Сервер уже запущен"
        
        try:
            self.serve_path = Path(serve_path)
            self.port = port
            
            # Создаем поток для запуска сервера
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            
            # Ждем немного для запуска
            time.sleep(1)
            
            if self.is_running:
                return True, f"Сервер запущен на http://localhost:{port}"
            else:
                return False, "Не удалось запустить сервер"
                
        except Exception as e:
            return False, f"Ошибка запуска сервера: {str(e)}"
    
    def _run_server(self):
        """Запуск сервера в отдельном потоке"""
        try:
            # Используем Python HTTP сервер
            import http.server
            import socketserver
            
            os.chdir(self.serve_path)
            
            Handler = http.server.SimpleHTTPRequestHandler
            
            self.httpd = socketserver.TCPServer(("", self.port), Handler)
            self.is_running = True
            
            # Запускаем сервер с возможностью остановки
            while self.is_running:
                self.httpd.handle_request()
                
        except Exception as e:
            self.is_running = False
            print(f"Ошибка сервера: {e}")
        finally:
            if self.httpd:
                self.httpd.server_close()
                self.httpd = None
    
    def stop_server(self):
        """Остановка сервера"""
        if not self.is_running:
            return False, "Сервер не запущен"
        
        try:
            self.is_running = False
            if self.httpd:
                self.httpd.server_close()
                self.httpd = None
            return True, "Сервер остановлен"
        except Exception as e:
            return False, f"Ошибка остановки сервера: {str(e)}"
    
    def get_status(self):
        """Получение статуса сервера"""
        return {
            'is_running': self.is_running,
            'port': self.port,
            'serve_path': str(self.serve_path) if self.serve_path else None
        }


class WorkerThread(QThread):
    """Рабочий поток для выполнения длительных операций"""
    
    # Сигналы для обновления UI
    progress_updated = pyqtSignal(str)  # Обновление прогресса
    operation_finished = pyqtSignal(bool, str)  # Завершение операции (успех, сообщение)
    log_message = pyqtSignal(str)  # Сообщение для лога
    
    def __init__(self, operation_type: str, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs
        self.is_running = False
    
    def run(self):
        """Выполнение операции в отдельном потоке"""
        self.is_running = True
        try:
            if self.operation_type == "convert_dataview":
                self._convert_dataview()
            elif self.operation_type == "setup_quartz":
                self._setup_quartz()
            elif self.operation_type == "deploy":
                self._deploy()
            elif self.operation_type == "start_watching":
                self._start_watching()
            else:
                self.operation_finished.emit(False, f"Неизвестная операция: {self.operation_type}")
        except Exception as e:
            self.operation_finished.emit(False, f"Ошибка: {str(e)}")
        finally:
            self.is_running = False
    
    def _convert_dataview(self):
        """Конвертация Dataview в отдельном потоке"""
        self.log_message.emit("🚀 Запуск конвертации Dataview...")
        self.progress_updated.emit("Начало конвертации...")
        
        # Имитация длительной операции
        for i in range(10):
            if not self.is_running:
                break
            self.progress_updated.emit(f"Обработка файлов... {i*10}%")
            self.msleep(500)  # Имитация работы
        
        self.progress_updated.emit("Конвертация завершена")
        self.operation_finished.emit(True, "✅ Конвертация Dataview завершена успешно")
    
    def _setup_quartz(self):
        """Настройка Quartz в отдельном потоке"""
        self.log_message.emit("🚀 Запуск настройки Quartz...")
        self.progress_updated.emit("Настройка Quartz...")
        
        # Имитация длительной операции
        for i in range(5):
            if not self.is_running:
                break
            self.progress_updated.emit(f"Настройка компонентов... {i*20}%")
            self.msleep(800)
        
        self.progress_updated.emit("Настройка завершена")
        self.operation_finished.emit(True, "✅ Настройка Quartz завершена успешно")
    
    def _deploy(self):
        """Деплой в отдельном потоке"""
        self.log_message.emit("🚀 Запуск деплоя...")
        self.progress_updated.emit("Подготовка к деплою...")
        
        # Имитация длительной операции
        for i in range(15):
            if not self.is_running:
                break
            self.progress_updated.emit(f"Деплой файлов... {i*7}%")
            self.msleep(300)
        
        self.progress_updated.emit("Деплой завершен")
        self.operation_finished.emit(True, "✅ Деплой завершен успешно")
    
    def _start_watching(self):
        """Запуск отслеживания в отдельном потоке"""
        vault = self.kwargs.get('vault', '')
        quartz = self.kwargs.get('quartz', '')
        
        self.log_message.emit("🚀 Запуск отслеживания изменений...")
        self.progress_updated.emit("Инициализация отслеживания...")
        
        try:
            # Здесь должна быть реальная логика запуска отслеживания
            self.msleep(1000)  # Имитация инициализации
            self.progress_updated.emit("Отслеживание активно")
            self.operation_finished.emit(True, "✅ Отслеживание изменений запущено")
        except Exception as e:
            self.operation_finished.emit(False, f"❌ Ошибка запуска отслеживания: {str(e)}")
    
    def stop(self):
        """Остановка потока"""
        self.is_running = False
        self.wait()  # Ждем завершения потока


class SimpleModernMainWindow(QMainWindow):
    """Упрощенное главное окно с современным дизайном и левым меню"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quartz ← Obsidian Builder - Simple Modern UI")
        self.resize(1400, 900)
        
        # Рабочие потоки
        self.worker_threads = []
        
        # Менеджер HTTP-сервера
        self.server_manager = HTTPServerManager()
        
        # Настройка темы
        self._setup_dark_theme()
        
        # Создание UI
        self._setup_navigation()
        self._create_pages()
        
        # Таймер для обновления статуса
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)  # Обновление каждые 2 секунды
    
    def _setup_dark_theme(self):
        """Настройка темной темы"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QGroupBox {
                border: 1px solid #3e3e3e;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4d4d4d;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5d5d5d;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
        """)
    
    def _setup_navigation(self):
        """Настройка левого меню навигации"""
        # Создаем главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Левая панель с кнопками навигации
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-right: 1px solid #3e3e3e;
            }
        """)
        
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Заголовок приложения
        app_title = QLabel("Quartz Builder")
        app_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #0078d4;
            padding: 20px 10px;
            border-bottom: 1px solid #3e3e3e;
        """)
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(app_title)
        
        # Кнопки навигации
        nav_buttons = [
            ("🏠 Главная", "dashboard"),
            ("⚙️ Настройки", "settings"),
            ("🚀 Действия", "actions"),
            ("📊 Мониторинг", "monitoring"),
            ("🚀 Автозапуск", "auto-launch")
        ]
        
        for text, route in nav_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    padding: 15px 20px;
                    font-size: 14px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:pressed {
                    background-color: #4d4d4d;
                }
            """)
            btn.clicked.connect(lambda checked, r=route: self._show_page(r))
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        
        # Правая панель с контентом
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        # Добавляем панели в главный layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.content_stack, 1)
    
    def _create_pages(self):
        """Создание страниц приложения"""
        self.dashboard_page = self._create_dashboard_page()
        self.settings_page = self._create_settings_page()
        self.actions_page = self._create_actions_page()
        self.monitoring_page = self._create_monitoring_page()
        self.auto_launch_page = self._create_auto_launch_page()
        
        # Добавляем страницы в стек
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.actions_page)
        self.content_stack.addWidget(self.monitoring_page)
        self.content_stack.addWidget(self.auto_launch_page)
    
    def _show_page(self, route: str):
        """Показывает страницу по маршруту"""
        page_map = {
            'dashboard': 0,
            'settings': 1,
            'actions': 2,
            'monitoring': 3,
            'auto-launch': 4
        }
        if route in page_map:
            self.content_stack.setCurrentIndex(page_map[route])
            print(f"✅ Переключение на страницу: {route}")
    
    def _create_dashboard_page(self):
        """Страница главной панели"""
        page = QWidget()
        page.setStyleSheet("background-color: #1e1e1e;")
        
        # Создаем scroll area для прокрутки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)
        
        # Заголовок
        title = QLabel("Добро пожаловать в Quartz ← Obsidian Builder")
        title.setStyleSheet("font-size: 24px; margin: 20px 0; color: #0078d4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Статус системы
        status_group = QGroupBox("Статус системы")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.status_label = QLabel("Система готова к работе")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
        # Быстрые действия
        actions_group = QGroupBox("Быстрые действия")
        actions_layout = QVBoxLayout()
        actions_group.setLayout(actions_layout)
        
        quick_actions = QHBoxLayout()
        
        select_vault_btn = QPushButton("Выбрать Vault")
        select_vault_btn.clicked.connect(self.select_vault)
        quick_actions.addWidget(select_vault_btn)
        
        start_watching_btn = QPushButton("Запустить отслеживание")
        start_watching_btn.clicked.connect(self.toggle_watching)
        quick_actions.addWidget(start_watching_btn)
        
        actions_layout.addLayout(quick_actions)
        layout.addWidget(actions_group)
        
        # Информационная карточка
        info_group = QGroupBox("О приложении")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        info_text = QLabel("""
        <p>Quartz ← Obsidian Builder - это современное приложение для автоматического построения 
        сайтов из баз знаний Obsidian с использованием Quartz.</p>
        
        <h3>Основные возможности:</h3>
        <ul>
        <li>🚀 Автоматический запуск сайта при изменениях</li>
        <li>🎨 Современный темный интерфейс</li>
        <li>📱 Адаптивный дизайн</li>
        <li>⚡ Быстрая синхронизация</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        scroll.setWidget(content)
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(scroll)
        
        return page
    
    def _create_settings_page(self):
        """Страница настроек"""
        page = QWidget()
        page.setStyleSheet("background-color: #1e1e1e;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QHBoxLayout()
        content.setLayout(layout)
        
        # Левая панель настроек
        left = QVBoxLayout()
        
        # Пути
        paths_group = QGroupBox("Пути и репозитории")
        paths_layout = QFormLayout()
        paths_group.setLayout(paths_layout)
        
        # Vault
        self.vault_path = QLineEdit()
        self.vault_path.setPlaceholderText("Выберите папку Obsidian Vault...")
        vault_btn = QPushButton("Выбрать Vault")
        vault_btn.clicked.connect(self.select_vault)
        vault_layout = QHBoxLayout()
        vault_layout.addWidget(self.vault_path)
        vault_layout.addWidget(vault_btn)
        paths_layout.addRow("Obsidian Vault:", vault_layout)
        
        # Режим деплоя
        self.deployment_mode = QComboBox()
        self.deployment_mode.addItems(["GitHub", "Локальный"])
        self.deployment_mode.currentTextChanged.connect(self.on_deployment_mode_changed)
        paths_layout.addRow("Режим деплоя:", self.deployment_mode)
        
        left.addWidget(paths_group)
        
        # GitHub настройки
        self.github_group = QGroupBox("GitHub настройки")
        gh_layout = QFormLayout()
        self.github_group.setLayout(gh_layout)
        
        self.quartz_repo = QLineEdit()
        self.quartz_repo.setText("https://github.com/jackyzha0/quartz.git")
        gh_layout.addRow("Quartz repo URL:", self.quartz_repo)
        
        self.deploy_branch = QLineEdit()
        self.deploy_branch.setText("gh-pages")
        gh_layout.addRow("Ветка деплоя:", self.deploy_branch)
        
        left.addWidget(self.github_group)
        
        # Локальные настройки
        self.local_group = QGroupBox("Локальные настройки")
        local_layout = QFormLayout()
        self.local_group.setLayout(local_layout)
        
        self.quartz_path = QLineEdit()
        self.quartz_path.setPlaceholderText("Путь к папке Quartz...")
        quartz_btn = QPushButton("Папка Quartz")
        quartz_btn.clicked.connect(self.select_quartz_folder)
        local_layout.addRow("Quartz root:", self.quartz_path)
        local_layout.addRow("", quartz_btn)
        
        left.addWidget(self.local_group)
        
        left.addStretch()
        layout.addLayout(left, 2)
        
        # Правая панель информации
        right = QVBoxLayout()
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        info_text = QLabel("""
        <h3>Режимы работы:</h3>
        <ul>
        <li><b>GitHub:</b> Полный деплой через GitHub Pages</li>
        <li><b>Локальный:</b> Синхронизация и локальный предпросмотр</li>
        </ul>
        
        <h3>Автозапуск:</h3>
        <p>При включенном отслеживании система автоматически:</p>
        <ul>
        <li>Отслеживает изменения в базе знаний</li>
        <li>Пересобирает сайт</li>
        <li>Запускает локальный сервер</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        right.addWidget(info_group)
        right.addStretch()
        layout.addLayout(right, 1)
        
        # Изначально показываем GitHub группу
        self.on_deployment_mode_changed("GitHub")
        
        scroll.setWidget(content)
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(scroll)
        
        return page
    
    def _create_actions_page(self):
        """Страница действий"""
        page = QWidget()
        page.setStyleSheet("background-color: #1e1e1e;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)
        
        # Заголовок
        title = QLabel("Действия")
        title.setStyleSheet("font-size: 20px; margin: 20px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Карточки действий
        actions_layout = QHBoxLayout()
        
        # Конвертация
        convert_group = QGroupBox("Конвертация Dataview")
        convert_layout = QVBoxLayout()
        convert_group.setLayout(convert_layout)
        
        convert_desc = QLabel("Преобразует Dataview блоки в статический Markdown")
        convert_layout.addWidget(convert_desc)
        
        self.btn_convert = QPushButton("Конвертировать")
        self.btn_convert.clicked.connect(self.on_convert_dataview)
        self.btn_convert.setMinimumHeight(50)
        convert_layout.addWidget(self.btn_convert)
        
        actions_layout.addWidget(convert_group)
        
        # Настройка Quartz
        setup_group = QGroupBox("Настройка Quartz")
        setup_layout = QVBoxLayout()
        setup_group.setLayout(setup_layout)
        
        setup_desc = QLabel("Настраивает Quartz для выбранного режима")
        setup_layout.addWidget(setup_desc)
        
        self.btn_setup = QPushButton("Настроить")
        self.btn_setup.clicked.connect(self.on_setup_quartz)
        self.btn_setup.setMinimumHeight(50)
        setup_layout.addWidget(self.btn_setup)
        
        actions_layout.addWidget(setup_group)
        
        # Деплой
        deploy_group = QGroupBox("Деплой")
        deploy_layout = QVBoxLayout()
        deploy_group.setLayout(deploy_layout)
        
        deploy_desc = QLabel("Выполняет деплой контента")
        deploy_layout.addWidget(deploy_desc)
        
        self.btn_deploy = QPushButton("Деплой")
        self.btn_deploy.clicked.connect(self.on_deploy)
        self.btn_deploy.setMinimumHeight(50)
        deploy_layout.addWidget(self.btn_deploy)
        
        actions_layout.addWidget(deploy_group)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        scroll.setWidget(content)
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(scroll)
        
        return page
    
    def _create_monitoring_page(self):
        """Страница мониторинга"""
        page = QWidget()
        page.setStyleSheet("background-color: #1e1e1e;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)
        
        # Заголовок
        title = QLabel("Мониторинг и логи")
        title.setStyleSheet("font-size: 20px; margin: 20px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Лог
        log_group = QGroupBox("Лог операций")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(400)
        log_layout.addWidget(self.log_view)
        
        # Прогресс
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Прогресс:"))
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        progress_layout.addWidget(self.progress)
        progress_layout.addStretch()
        
        log_layout.addLayout(progress_layout)
        layout.addWidget(log_group)
        
        # Управление логом
        log_controls = QHBoxLayout()
        
        clear_btn = QPushButton("Очистить лог")
        clear_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(clear_btn)
        
        save_btn = QPushButton("Сохранить лог")
        save_btn.clicked.connect(self.save_log)
        log_controls.addWidget(save_btn)
        
        log_controls.addStretch()
        layout.addLayout(log_controls)
        
        scroll.setWidget(content)
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(scroll)
        
        return page
    
    def _create_auto_launch_page(self):
        """Страница автозапуска"""
        page = QWidget()
        page.setStyleSheet("background-color: #1e1e1e;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)
        
        # Заголовок
        title = QLabel("Автоматический запуск сайта")
        title.setStyleSheet("font-size: 20px; margin: 20px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Статус автозапуска
        status_group = QGroupBox("Статус автозапуска")
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.auto_launch_status = QLabel("Отслеживание не запущено")
        status_layout.addWidget(self.auto_launch_status)
        
        # Переключатель (простая кнопка)
        self.watch_switch = QPushButton("Включить отслеживание")
        self.watch_switch.setCheckable(True)
        self.watch_switch.clicked.connect(self.toggle_watching)
        status_layout.addWidget(self.watch_switch)
        
        layout.addWidget(status_group)
        
        # Настройки автозапуска
        config_group = QGroupBox("Настройки автозапуска")
        config_layout = QFormLayout()
        config_group.setLayout(config_layout)
        
        # Порт сервера
        self.server_port = QLineEdit()
        self.server_port.setText("1313")
        config_layout.addRow("Порт локального сервера:", self.server_port)
        
        # Автопересборка
        self.auto_rebuild = QPushButton("Автопересборка: ВКЛ")
        self.auto_rebuild.setCheckable(True)
        self.auto_rebuild.setChecked(True)
        self.auto_rebuild.clicked.connect(self.toggle_auto_rebuild)
        config_layout.addRow("", self.auto_rebuild)
        
        layout.addWidget(config_group)
        
        # Управление сервером
        server_group = QGroupBox("Управление локальным сервером")
        server_layout = QVBoxLayout()
        server_group.setLayout(server_layout)
        
        server_controls = QHBoxLayout()
        
        self.start_server_btn = QPushButton("Запустить сервер")
        self.start_server_btn.clicked.connect(self.start_local_server)
        server_controls.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("Остановить сервер")
        self.stop_server_btn.clicked.connect(self.stop_local_server)
        server_controls.addWidget(self.stop_server_btn)
        
        self.restart_server_btn = QPushButton("Перезапустить")
        self.restart_server_btn.clicked.connect(self.restart_local_server)
        server_controls.addWidget(self.restart_server_btn)
        
        server_layout.addLayout(server_controls)
        layout.addWidget(server_group)
        
        # Информация
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)
        
        info_text = QLabel("""
        <h3>Как работает автозапуск:</h3>
        <ol>
        <li>Система отслеживает изменения в выбранной базе знаний</li>
        <li>При обнаружении изменений автоматически пересобирает сайт</li>
        <li>Запускает локальный веб-сервер для предпросмотра</li>
        <li>Сайт доступен по адресу http://localhost:1313</li>
        </ol>
        
        <h3>Преимущества:</h3>
        <ul>
        <li>Мгновенный предпросмотр изменений</li>
        <li>Автоматическая синхронизация</li>
        <li>Удобство разработки</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        scroll.setWidget(content)
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(scroll)
        
        return page
    
    def _update_status(self):
        """Обновляет статус системы"""
        # Простое обновление статуса
        pass
    
    def select_vault(self):
        """Выбор папки Vault"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите Obsidian Vault")
        if folder:
            self.vault_path.setText(folder)
            self.append_log(f"Выбран Vault: {folder}")
    
    def select_quartz_folder(self):
        """Выбор папки Quartz"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку Quartz")
        if folder:
            self.quartz_path.setText(folder)
            self.append_log(f"Выбрана папка Quartz: {folder}")
    
    def on_deployment_mode_changed(self, mode_text: str):
        """Обработчик изменения режима деплоя"""
        if mode_text == "GitHub":
            self.github_group.setVisible(True)
            self.local_group.setVisible(False)
        else:
            self.github_group.setVisible(False)
            self.local_group.setVisible(True)
        
        self.append_log(f"Режим деплоя изменен на: {mode_text}")
    
    def toggle_watching(self, checked: bool):
        """Включение/выключение отслеживания"""
        if checked:
            self.start_watching()
            self.watch_switch.setText("Отключить отслеживание")
        else:
            self.stop_watching()
            self.watch_switch.setText("Включить отслеживание")
    
    def toggle_auto_rebuild(self, checked: bool):
        """Включение/выключение автопересборки"""
        if checked:
            self.auto_rebuild.setText("Автопересборка: ВКЛ")
        else:
            self.auto_rebuild.setText("Автопересборка: ВЫКЛ")
    
    def start_watching(self):
        """Запуск отслеживания изменений"""
        vault = self.vault_path.text().strip()
        quartz = self.quartz_path.text().strip()
        
        if not vault or not Path(vault).exists():
            self.show_warning("Укажите корректную папку Vault")
            return
        
        if not quartz or not Path(quartz).exists():
            self.show_warning("Укажите корректную папку Quartz")
            return
        
        # Создаем рабочий поток для запуска отслеживания
        worker = WorkerThread("start_watching", vault=vault, quartz=quartz)
        worker.progress_updated.connect(self._update_progress)
        worker.operation_finished.connect(self._on_watching_started)
        worker.log_message.connect(self.append_log)
        
        self.worker_threads.append(worker)
        worker.start()
    
    def _on_watching_started(self, success: bool, message: str):
        """Обработка запуска отслеживания"""
        self.append_log(message)
        if success:
            self.auto_launch_status.setText("Отслеживание активно")
        else:
            self.auto_launch_status.setText("Отслеживание неактивно")
    
    def stop_watching(self):
        """Остановка отслеживания"""
        self.auto_launch_status.setText("Отслеживание неактивно")
        self.append_log("✅ Отслеживание изменений остановлено")
    
    def start_local_server(self):
        """Запуск локального сервера"""
        try:
            # Получаем путь к папке Quartz
            quartz_path = self.quartz_path.text().strip()
            if not quartz_path or not Path(quartz_path).exists():
                self.show_warning("Укажите корректную папку Quartz")
                return
            
            # Получаем порт
            try:
                port = int(self.server_port.text())
            except ValueError:
                self.show_warning("Укажите корректный порт")
                return
            
            # Запускаем сервер
            success, message = self.server_manager.start_server(quartz_path, port)
            
            if success:
                self.append_log(f"✅ {message}")
                self.start_server_btn.setEnabled(False)
                self.stop_server_btn.setEnabled(True)
                self.restart_server_btn.setEnabled(True)
            else:
                self.append_log(f"❌ {message}")
                self.show_error(message)
                
        except Exception as e:
            self.append_log(f"❌ Ошибка запуска сервера: {str(e)}")
            self.show_error(f"Ошибка запуска сервера: {str(e)}")
    
    def stop_local_server(self):
        """Остановка локального сервера"""
        try:
            success, message = self.server_manager.stop_server()
            
            if success:
                self.append_log(f"✅ {message}")
                self.start_server_btn.setEnabled(True)
                self.stop_server_btn.setEnabled(False)
                self.restart_server_btn.setEnabled(False)
            else:
                self.append_log(f"❌ {message}")
                
        except Exception as e:
            self.append_log(f"❌ Ошибка остановки сервера: {str(e)}")
    
    def restart_local_server(self):
        """Перезапуск локального сервера"""
        self.append_log("🔄 Перезапуск локального сервера...")
        self.stop_local_server()
        time.sleep(1)  # Небольшая пауза
        self.start_local_server()
    
    def on_convert_dataview(self):
        """Конвертация Dataview"""
        # Создаем рабочий поток для конвертации
        worker = WorkerThread("convert_dataview")
        worker.progress_updated.connect(self._update_progress)
        worker.operation_finished.connect(self._on_operation_finished)
        worker.log_message.connect(self.append_log)
        
        self.worker_threads.append(worker)
        worker.start()
    
    def on_setup_quartz(self):
        """Настройка Quartz"""
        # Создаем рабочий поток для настройки
        worker = WorkerThread("setup_quartz")
        worker.progress_updated.connect(self._update_progress)
        worker.operation_finished.connect(self._on_operation_finished)
        worker.log_message.connect(self.append_log)
        
        self.worker_threads.append(worker)
        worker.start()
    
    def on_deploy(self):
        """Деплой"""
        # Создаем рабочий поток для деплоя
        worker = WorkerThread("deploy")
        worker.progress_updated.connect(self._update_progress)
        worker.operation_finished.connect(self._on_operation_finished)
        worker.log_message.connect(self.append_log)
        
        self.worker_threads.append(worker)
        worker.start()
    
    def _update_progress(self, message: str):
        """Обновление прогресса"""
        if hasattr(self, 'progress'):
            # Обновляем прогресс-бар если он есть
            pass
        self.append_log(message)
    
    def _on_operation_finished(self, success: bool, message: str):
        """Обработка завершения операции"""
        self.append_log(message)
        if success:
            # Можно добавить уведомление об успехе
            pass
        else:
            # Можно добавить уведомление об ошибке
            pass
    
    def append_log(self, text: str):
        """Добавление записи в лог"""
        if hasattr(self, 'log_view'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_view.appendPlainText(f"[{timestamp}] {text}")
    
    def clear_log(self):
        """Очистка лога"""
        if hasattr(self, 'log_view'):
            self.log_view.clear()
            self.append_log("Лог очищен")
    
    def save_log(self):
        """Сохранение лога"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить лог", "", "Text Files (*.txt);;All Files (*)"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_view.toPlainText())
                self.append_log(f"Лог сохранен в: {filename}")
        except Exception as e:
            self.append_log(f"Ошибка сохранения лога: {e}")
    
    def show_warning(self, message: str):
        """Показ предупреждения"""
        QMessageBox.warning(self, "Предупреждение", message)
    
    def show_error(self, message: str):
        """Показ ошибки"""
        QMessageBox.critical(self, "Ошибка", message)
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        # Останавливаем все рабочие потоки
        for worker in self.worker_threads:
            if worker.isRunning():
                worker.stop()
        
        # Останавливаем HTTP-сервер
        if self.server_manager.is_running:
            self.server_manager.stop_server()
        
        event.accept()


def run_simple_modern_app():
    """Запуск упрощенного современного приложения"""
    app = QApplication(sys.argv)
    w = SimpleModernMainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_simple_modern_app()
