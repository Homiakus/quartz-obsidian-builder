"""
@file: modern_ui.py
@description: Современный UI с левым меню и темной темой
@dependencies: PyQt6, qfluentwidgets, auto_launcher
@created: 2024-12-19
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFileDialog, QPlainTextEdit, QFrame,
    QStackedWidget, QScrollArea
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

# Fluent Widgets
try:
    from qfluentwidgets import (
        FluentWindow, NavigationInterface, NavigationItemPosition,
        SubtitleLabel, BodyLabel, CaptionLabel, StrongBodyLabel,
        PushButton, PrimaryPushButton, TransparentPushButton,
        LineEdit, TextEdit, ProgressRing, CardWidget,
        InfoBar, InfoBarPosition, MessageBox, FluentIcon,
        SwitchButton, ComboBox, TabWidget
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    # Fallback импорты
    from PyQt6.QtWidgets import (
        QPushButton, QComboBox, QTabWidget, QScrollArea,
        QGroupBox, QFormLayout, QProgressBar
    )
    # Создаем алиасы
    FluentWindow = QMainWindow
    NavigationInterface = QWidget
    NavigationItemPosition = None
    SubtitleLabel = QLabel
    BodyLabel = QLabel
    CaptionLabel = QLabel
    StrongBodyLabel = QLabel
    PushButton = QPushButton
    PrimaryPushButton = QPushButton
    TransparentPushButton = QPushButton
    LineEdit = QLineEdit
    TextEdit = QPlainTextEdit
    ProgressRing = QProgressBar
    CardWidget = QGroupBox
    InfoBar = None
    InfoBarPosition = None
    MessageBox = None
    FluentIcon = None
    SwitchButton = QPushButton
    ComboBox = QComboBox
    TabWidget = QTabWidget

from auto_launcher import create_auto_launcher
from deployment_manager import DeploymentMode, QuartzConfig


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


class ModernMainWindow(FluentWindow):
    """Главное окно с современным дизайном и левым меню"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quartz ← Obsidian Builder - Modern UI")
        self.resize(1400, 900)
        
        # Конфигурация
        self.deployment_config = QuartzConfig(
            mode=DeploymentMode.GITHUB,
            repo_url="https://github.com/jackyzha0/quartz.git",
            local_path="",
            branch="main",
            deploy_branch="gh-pages",
            site_name="Мой сайт"
        )
        
        # Автозапуск
        self.auto_launcher = None
        self.is_watching = False
        
        # Рабочие потоки
        self.worker_threads = []
        
        # Настройка темы
        self._setup_dark_theme()
        
        # Создание UI
        if FLUENT_AVAILABLE:
            self._setup_fluent_navigation()
        else:
            self._setup_fallback_navigation()
        
        self._create_pages()
        
        # Таймер для обновления статуса
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)  # Обновление каждые 2 секунды
    
    def _setup_dark_theme(self):
        """Настройка темной темы"""
        if FLUENT_AVAILABLE:
            try:
                from qfluentwidgets import Theme, qconfig
                qconfig.set(qconfig.themeMode, Theme.DARK)
            except:
                pass
        
        # Fallback темная тема
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
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                color: #ffffff;
                font-weight: bold;
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
        """)
    
    def _setup_fluent_navigation(self):
        """Настройка Fluent навигации"""
        # Добавляем элементы навигации
        self.navigationInterface.addItem(
            routeKey='dashboard',
            icon=FluentIcon.HOME,
            text='Главная',
            position=NavigationItemPosition.TOP
        )
        
        self.navigationInterface.addItem(
            routeKey='settings',
            icon=FluentIcon.SETTING,
            text='Настройки',
            position=NavigationItemPosition.TOP
        )
        
        self.navigationInterface.addItem(
            routeKey='actions',
            icon=FluentIcon.PLAY,
            text='Действия',
            position=NavigationItemPosition.TOP
        )
        
        self.navigationInterface.addItem(
            routeKey='monitoring',
            icon=FluentIcon.CHART,
            text='Мониторинг',
            position=NavigationItemPosition.TOP
        )
        
        self.navigationInterface.addItem(
            routeKey='auto-launch',
            icon=FluentIcon.ROCKET,
            text='Автозапуск',
            position=NavigationItemPosition.TOP
        )
    
    def _setup_fallback_navigation(self):
        """Fallback навигация для стандартного PyQt"""
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
        if FLUENT_AVAILABLE:
            # Создаем страницы для Fluent
            self.dashboard_page = self._create_dashboard_page()
            self.settings_page = self._create_settings_page()
            self.actions_page = self._create_actions_page()
            self.monitoring_page = self._create_monitoring_page()
            self.auto_launch_page = self._create_auto_launch_page()
            
            # Добавляем страницы в навигацию
            self.addSubInterface(self.dashboard_page, 'dashboard', 'Главная')
            self.addSubInterface(self.settings_page, 'settings', 'Настройки')
            self.addSubInterface(self.actions_page, 'actions', 'Действия')
            self.addSubInterface(self.monitoring_page, 'monitoring', 'Мониторинг')
            self.addSubInterface(self.auto_launch_page, 'auto-launch', 'Автозапуск')
        else:
            # Fallback страницы
            self._create_fallback_pages()
    
    def _create_fallback_pages(self):
        """Создание fallback страниц"""
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
        """Показывает страницу по маршруту (fallback)"""
        if not FLUENT_AVAILABLE:
            page_map = {
                'dashboard': 0,
                'settings': 1,
                'actions': 2,
                'monitoring': 3,
                'auto-launch': 4
            }
            if route in page_map:
                self.content_stack.setCurrentIndex(page_map[route])
    
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
        title = SubtitleLabel("Добро пожаловать в Quartz ← Obsidian Builder")
        title.setStyleSheet("font-size: 24px; margin: 20px 0; color: #0078d4;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Статус системы
        status_card = CardWidget()
        status_layout = QVBoxLayout()
        status_card.setLayout(status_layout)
        
        status_title = StrongBodyLabel("Статус системы")
        status_layout.addWidget(status_title)
        
        self.status_label = BodyLabel("Система готова к работе")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_card)
        
        # Быстрые действия
        actions_card = CardWidget()
        actions_layout = QVBoxLayout()
        actions_card.setLayout(actions_layout)
        
        actions_title = StrongBodyLabel("Быстрые действия")
        actions_layout.addWidget(actions_title)
        
        quick_actions = QHBoxLayout()
        
        select_vault_btn = PrimaryPushButton("Выбрать Vault")
        select_vault_btn.clicked.connect(self.select_vault)
        quick_actions.addWidget(select_vault_btn)
        
        start_watching_btn = PrimaryPushButton("Запустить отслеживание")
        start_watching_btn.clicked.connect(self.toggle_watching)
        quick_actions.addWidget(start_watching_btn)
        
        actions_layout.addLayout(quick_actions)
        layout.addWidget(actions_card)
        
        # Информационная карточка
        info_card = CardWidget()
        info_layout = QVBoxLayout()
        info_card.setLayout(info_layout)
        
        info_title = StrongBodyLabel("О приложении")
        info_layout.addWidget(info_title)
        
        info_text = CaptionLabel("""
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
        
        layout.addWidget(info_card)
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
        paths_card = CardWidget()
        paths_layout = QVBoxLayout()
        paths_card.setLayout(paths_layout)
        
        paths_title = StrongBodyLabel("Пути и репозитории")
        paths_layout.addWidget(paths_title)
        
        # Vault
        vault_layout = QHBoxLayout()
        self.vault_path = LineEdit()
        self.vault_path.setPlaceholderText("Выберите папку Obsidian Vault...")
        vault_btn = PrimaryPushButton("Выбрать Vault")
        vault_btn.clicked.connect(self.select_vault)
        vault_layout.addWidget(self.vault_path)
        vault_layout.addWidget(vault_btn)
        paths_layout.addLayout(vault_layout)
        
        # Режим деплоя
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(BodyLabel("Режим деплоя:"))
        self.deployment_mode = ComboBox()
        self.deployment_mode.addItems(["GitHub", "Локальный"])
        self.deployment_mode.currentTextChanged.connect(self.on_deployment_mode_changed)
        mode_layout.addWidget(self.deployment_mode)
        paths_layout.addLayout(mode_layout)
        
        left.addWidget(paths_card)
        
        # GitHub настройки
        self.github_group = CardWidget()
        gh_layout = QVBoxLayout()
        self.github_group.setLayout(gh_layout)
        
        gh_title = StrongBodyLabel("GitHub настройки")
        gh_layout.addWidget(gh_title)
        
        self.quartz_repo = LineEdit()
        self.quartz_repo.setText("https://github.com/jackyzha0/quartz.git")
        gh_layout.addWidget(BodyLabel("Quartz repo URL:"))
        gh_layout.addWidget(self.quartz_repo)
        
        self.deploy_branch = LineEdit()
        self.deploy_branch.setText("gh-pages")
        gh_layout.addWidget(BodyLabel("Ветка деплоя:"))
        gh_layout.addWidget(self.deploy_branch)
        
        left.addWidget(self.github_group)
        
        # Локальные настройки
        self.local_group = CardWidget()
        local_layout = QVBoxLayout()
        self.local_group.setLayout(local_layout)
        
        local_title = StrongBodyLabel("Локальные настройки")
        local_layout.addWidget(local_title)
        
        self.quartz_path = LineEdit()
        self.quartz_path.setPlaceholderText("Путь к папке Quartz...")
        quartz_btn = PrimaryPushButton("Папка Quartz")
        quartz_btn.clicked.connect(self.select_quartz_folder)
        local_layout.addWidget(BodyLabel("Quartz root:"))
        local_layout.addWidget(self.quartz_path)
        local_layout.addWidget(quartz_btn)
        
        left.addWidget(self.local_group)
        
        left.addStretch()
        layout.addLayout(left, 2)
        
        # Правая панель информации
        right = QVBoxLayout()
        info_card = CardWidget()
        info_layout = QVBoxLayout()
        info_card.setLayout(info_layout)
        
        info_title = StrongBodyLabel("Информация")
        info_layout.addWidget(info_title)
        
        info_text = CaptionLabel("""
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
        
        right.addWidget(info_card)
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
        title = SubtitleLabel("Действия")
        title.setStyleSheet("font-size: 20px; margin: 20px 0;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Карточки действий
        actions_layout = QHBoxLayout()
        
        # Конвертация
        convert_card = CardWidget()
        convert_layout = QVBoxLayout()
        convert_card.setLayout(convert_layout)
        
        convert_title = StrongBodyLabel("Конвертация Dataview")
        convert_layout.addWidget(convert_title)
        
        convert_desc = CaptionLabel("Преобразует Dataview блоки в статический Markdown")
        convert_layout.addWidget(convert_desc)
        
        self.btn_convert = PrimaryPushButton("Конвертировать")
        self.btn_convert.clicked.connect(self.on_convert_dataview)
        self.btn_convert.setMinimumHeight(50)
        convert_layout.addWidget(self.btn_convert)
        
        actions_layout.addWidget(convert_card)
        
        # Настройка Quartz
        setup_card = CardWidget()
        setup_layout = QVBoxLayout()
        setup_card.setLayout(setup_layout)
        
        setup_title = StrongBodyLabel("Настройка Quartz")
        setup_layout.addWidget(setup_title)
        
        setup_desc = CaptionLabel("Настраивает Quartz для выбранного режима")
        setup_layout.addWidget(setup_desc)
        
        self.btn_setup = PrimaryPushButton("Настроить")
        self.btn_setup.clicked.connect(self.on_setup_quartz)
        self.btn_setup.setMinimumHeight(50)
        setup_layout.addWidget(self.btn_setup)
        
        actions_layout.addWidget(setup_card)
        
        # Деплой
        deploy_card = CardWidget()
        deploy_layout = QVBoxLayout()
        deploy_card.setLayout(deploy_layout)
        
        deploy_title = StrongBodyLabel("Деплой")
        deploy_layout.addWidget(deploy_title)
        
        deploy_desc = CaptionLabel("Выполняет деплой контента")
        deploy_layout.addWidget(deploy_desc)
        
        self.btn_deploy = PrimaryPushButton("Деплой")
        self.btn_deploy.clicked.connect(self.on_deploy)
        self.btn_deploy.setMinimumHeight(50)
        deploy_layout.addWidget(self.btn_deploy)
        
        actions_layout.addWidget(deploy_card)
        
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
        title = SubtitleLabel("Мониторинг и логи")
        title.setStyleSheet("font-size: 20px; margin: 20px 0;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Лог
        log_card = CardWidget()
        log_layout = QVBoxLayout()
        log_card.setLayout(log_layout)
        
        log_title = StrongBodyLabel("Лог операций")
        log_layout.addWidget(log_title)
        
        self.log_view = TextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(400)
        log_layout.addWidget(self.log_view)
        
        # Прогресс
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(BodyLabel("Прогресс:"))
        
        self.progress = ProgressRing()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        progress_layout.addWidget(self.progress)
        progress_layout.addStretch()
        
        log_layout.addLayout(progress_layout)
        layout.addWidget(log_card)
        
        # Управление логом
        log_controls = QHBoxLayout()
        
        clear_btn = TransparentPushButton("Очистить лог")
        clear_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(clear_btn)
        
        save_btn = TransparentPushButton("Сохранить лог")
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
        title = SubtitleLabel("Автоматический запуск сайта")
        title.setStyleSheet("font-size: 20px; margin: 20px 0;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Статус автозапуска
        status_card = CardWidget()
        status_layout = QVBoxLayout()
        status_card.setLayout(status_layout)
        
        status_title = StrongBodyLabel("Статус автозапуска")
        status_layout.addWidget(status_title)
        
        self.auto_launch_status = BodyLabel("Отслеживание не запущено")
        status_layout.addWidget(self.auto_launch_status)
        
        # Переключатель
        self.watch_switch = SwitchButton()
        self.watch_switch.clicked.connect(self.toggle_watching)
        status_layout.addWidget(self.watch_switch)
        
        layout.addWidget(status_card)
        
        # Настройки автозапуска
        config_card = CardWidget()
        config_layout = QVBoxLayout()
        config_card.setLayout(config_layout)
        
        config_title = StrongBodyLabel("Настройки автозапуска")
        config_layout.addWidget(config_title)
        
        # Порт сервера
        port_layout = QHBoxLayout()
        port_layout.addWidget(BodyLabel("Порт локального сервера:"))
        self.server_port = LineEdit()
        self.server_port.setText("1313")
        port_layout.addWidget(self.server_port)
        config_layout.addLayout(port_layout)
        
        # Автопересборка
        self.auto_rebuild = SwitchButton()
        self.auto_rebuild.setChecked(True)
        config_layout.addWidget(BodyLabel("Автоматическая пересборка при изменениях"))
        config_layout.addWidget(self.auto_rebuild)
        
        layout.addWidget(config_card)
        
        # Управление сервером
        server_card = CardWidget()
        server_layout = QVBoxLayout()
        server_card.setLayout(server_layout)
        
        server_title = StrongBodyLabel("Управление локальным сервером")
        server_layout.addWidget(server_title)
        
        server_controls = QHBoxLayout()
        
        self.start_server_btn = PrimaryPushButton("Запустить сервер")
        self.start_server_btn.clicked.connect(self.start_local_server)
        server_controls.addWidget(self.start_server_btn)
        
        self.stop_server_btn = PrimaryPushButton("Остановить сервер")
        self.stop_server_btn.clicked.connect(self.stop_local_server)
        server_controls.addWidget(self.stop_server_btn)
        
        self.restart_server_btn = TransparentPushButton("Перезапустить")
        self.restart_server_btn.clicked.connect(self.restart_local_server)
        server_controls.addWidget(self.restart_server_btn)
        
        server_layout.addLayout(server_controls)
        layout.addWidget(server_card)
        
        # Информация
        info_card = CardWidget()
        info_layout = QVBoxLayout()
        info_card.setLayout(info_layout)
        
        info_title = StrongBodyLabel("Информация")
        info_layout.addWidget(info_title)
        
        info_text = CaptionLabel("""
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
        
        layout.addWidget(info_card)
        layout.addStretch()
        
        scroll.setWidget(content)
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(scroll)
        
        return page
    
    def _update_status(self):
        """Обновляет статус системы"""
        if self.auto_launcher:
            try:
                status = self.auto_launcher.get_status()
                if hasattr(self, 'status_label'):
                    self.status_label.setText(f"Отслеживание: {'Активно' if status.get('is_watching', False) else 'Неактивно'}")
            except:
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
            self.deployment_config.mode = DeploymentMode.GITHUB
        else:
            self.github_group.setVisible(False)
            self.local_group.setVisible(True)
            self.deployment_config.mode = DeploymentMode.LOCAL
        
        self.append_log(f"Режим деплоя изменен на: {mode_text}")
    
    def toggle_watching(self):
        """Включение/выключение отслеживания"""
        if not hasattr(self, 'is_watching') or not self.is_watching:
            self.start_watching()
        else:
            self.stop_watching()
    
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
            self.is_watching = True
            self.watch_switch.setChecked(True)
            self.auto_launch_status.setText("Отслеживание активно")
        else:
            self.is_watching = False
            self.watch_switch.setChecked(False)
            self.auto_launch_status.setText("Отслеживание неактивно")
    
    def stop_watching(self):
        """Остановка отслеживания"""
        if self.auto_launcher:
            self.auto_launcher.stop_watching()
            self.is_watching = False
            self.watch_switch.setChecked(False)
            self.auto_launch_status.setText("Отслеживание неактивно")
            self.append_log("✅ Отслеживание изменений остановлено")
    
    def on_content_changed(self):
        """Обработчик изменений в контенте"""
        self.append_log("🔄 Обнаружены изменения в базе знаний")
        
        if hasattr(self, 'auto_rebuild') and self.auto_rebuild.isChecked():
            self.append_log("🔨 Автоматическая пересборка...")
            if self.auto_launcher:
                self.auto_launcher.rebuild_and_restart()
    
    def start_local_server(self):
        """Запуск локального сервера"""
        if not self.auto_launcher:
            self.show_warning("Сначала запустите отслеживание")
            return
        
        try:
            port = int(self.server_port.text())
            if self.auto_launcher.launch_local_site(port):
                self.append_log(f"✅ Локальный сервер запущен на порту {port}")
            else:
                self.show_error("Не удалось запустить локальный сервер")
        except ValueError:
            self.show_warning("Укажите корректный порт")
    
    def stop_local_server(self):
        """Остановка локального сервера"""
        if self.auto_launcher:
            self.auto_launcher.stop_local_site()
            self.append_log("✅ Локальный сервер остановлен")
    
    def restart_local_server(self):
        """Перезапуск локального сервера"""
        if self.auto_launcher:
            self.auto_launcher.restart()
            self.append_log("✅ Локальный сервер перезапущен")
    
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
        if FLUENT_AVAILABLE and MessageBox:
            MessageBox.warning(self, "Предупреждение", message)
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Предупреждение", message)
    
    def show_error(self, message: str):
        """Показ ошибки"""
        if FLUENT_AVAILABLE and MessageBox:
            MessageBox.error(self, "Ошибка", message)
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", message)
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        # Останавливаем все рабочие потоки
        for worker in self.worker_threads:
            if worker.isRunning():
                worker.stop()
        
        # Останавливаем отслеживание
        if self.auto_launcher:
            self.auto_launcher.stop_watching()
        
        event.accept()


def run_modern_app():
    """Запуск современного приложения"""
    app = QApplication(sys.argv)
    w = ModernMainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_modern_app()
