# gui.py
import sys
import os
from pathlib import Path
from datetime import datetime

# Конфигурационные константы
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 700
DEFAULT_QUARTZ_REPO = "https://github.com/jackyzha0/quartz.git"
DEFAULT_DEPLOY_BRANCH = "gh-pages"
DEFAULT_SITE_NAME = "Мой сайт"
DEFAULT_EXTRA_SETTINGS = "favicon.ico, custom.css"

# PyQt6 + Fluent Widgets
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFileDialog, QPlainTextEdit,
    QProgressBar, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Fluent Widgets - полная интеграция
try:
    from qfluentwidgets import (
        # Основные виджеты
        PushButton, ComboBox, SwitchButton, FluentIcon,
        InfoBar, InfoBarPosition, MessageBox,
        SubtitleLabel, BodyLabel, CaptionLabel,
        
        # Дополнительные Fluent виджеты
        CardWidget, PrimaryPushButton, TransparentPushButton,
        LineEdit, TextEdit, ProgressBar, ProgressRing,
        ScrollArea, ListWidget, TreeWidget, TabBar, TabItem,
        
        # Навигация и макет
        NavigationInterface, NavigationItemPosition,
        FluentWindow, SubtitleLabel, StrongBodyLabel,
        
        # Тема и конфигурация (правильный способ)
        Theme, qconfig, ConfigItem, OptionsConfigItem, BoolValidator,
        OptionsValidator, ColorConfigItem, ColorValidator, ColorSerializer
    )
    FLUENT_AVAILABLE = True
    print("✅ PyQt-Fluent-Widgets успешно импортирован")
except ImportError as e:
    print(f"❌ Ошибка импорта PyQt-Fluent-Widgets: {e}")
    FLUENT_AVAILABLE = False
    # Fallback к стандартным виджетам если Fluent недоступен
    from PyQt6.QtWidgets import QPushButton, QComboBox, QTabWidget, QScrollArea
    PushButton = QPushButton
    ComboBox = QComboBox
    SwitchButton = QPushButton
    CardWidget = QGroupBox
    PrimaryPushButton = QPushButton
    TransparentPushButton = QPushButton
    LineEdit = QLineEdit
    TextEdit = QPlainTextEdit
    ProgressBar = QProgressBar
    ProgressRing = QProgressBar
    TabWidget = QTabWidget
    ScrollArea = QScrollArea
    ListWidget = QWidget
    TreeWidget = QWidget
    NavigationInterface = QWidget
    NavigationItemPosition = None
    FluentWindow = QMainWindow
    SubtitleLabel = QLabel
    StrongBodyLabel = QLabel
    FluentIcon = None
    InfoBar = None
    InfoBarPosition = None
    MessageBox = QMessageBox
    BodyLabel = QLabel
    CaptionLabel = QLabel
    # Fallback для конфигурации
    Theme = None
    qconfig = None
    ConfigItem = None
    OptionsConfigItem = None
    BoolValidator = None
    OptionsValidator = None
    ColorConfigItem = None
    ColorValidator = None
    ColorSerializer = None
    FLUENT_AVAILABLE = False

# Импортируем бизнес-логику
from dataview_converter import convert_dataview_in_vault
from deployment_manager import (
    DeploymentMode, QuartzConfig, get_deployment_manager,
    SetupResult, DeployResult
)

# ---------- Конфигурация приложения ----------
if FLUENT_AVAILABLE:
    # Упрощенная конфигурация
    app_config = None
    print("ℹ️ Конфигурация qconfig временно отключена для упрощения")
else:
    app_config = None

# ---------- Вспомогательный QThread-воркер ----------
class WorkerThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, target_fn, *args, **kwargs):
        super().__init__()
        self.target_fn = target_fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # передаём logger как ключевой аргумент
            result = self.target_fn(*self.args, logger=self._emit_log, **self.kwargs)
            self.finished.emit(True, str(result or "Готово"))
        except Exception as e:
            self._emit_log(f"Ошибка: {e}")
            self.finished.emit(False, str(e))

    def _emit_log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.emit(f"[{timestamp}] {msg}")


# ---------- Главное окно ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quartz ← Obsidian Builder")
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        
        # конфигурация деплоя (инициализируем ДО _build_ui)
        self.deployment_config = QuartzConfig(
            mode=DeploymentMode.GITHUB,
            repo_url=DEFAULT_QUARTZ_REPO,
            local_path="",
            branch="main",
            deploy_branch=DEFAULT_DEPLOY_BRANCH,
            site_name=DEFAULT_SITE_NAME
        )
        
        # текущие worker-потоки
        self.current_worker = None
        
        # Настройка темы Fluent
        if FLUENT_AVAILABLE:
            self._setup_fluent_theme()
        
        self._build_ui()
    
    def _setup_fluent_theme(self):
        """Настройка Fluent темы"""
        try:
            # Устанавливаем темную тему
            qconfig.set(qconfig.themeMode, Theme.DARK)
            print("🎨 Темная тема установлена")
        except Exception as e:
            print(f"Ошибка настройки темы: {e}")

    def _build_ui(self):
        print(f"🔧 FLUENT_AVAILABLE = {FLUENT_AVAILABLE}")
        if FLUENT_AVAILABLE:
            print("🎨 Создаем Fluent UI интерфейс")
            self._build_fluent_ui()
        else:
            print("⚠️ Создаем Fallback UI интерфейс")
            self._build_fallback_ui()
    
    def _build_fluent_ui(self):
        """Создание Fluent UI интерфейса"""
        # Создаем центральный виджет с табами
        central = QWidget()
        if hasattr(self, 'setCentralWidget'):
            self.setCentralWidget(central)
        else:
            # Для FluentWindow используем другой подход
            self.setContentWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Заголовок приложения
        title = SubtitleLabel("Quartz ← Obsidian Builder")
        title.setObjectName("titleLabel")
        title.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #0078d4;
                margin: 20px 0;
            }
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Создаем табы для разных разделов
        from PyQt6.QtWidgets import QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabWidget")
        
        # Таб 1: Основные настройки
        self.settings_tab = self._create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Настройки")
        
        # Таб 2: Действия
        self.actions_tab = self._create_actions_tab()
        self.tab_widget.addTab(self.actions_tab, "🚀 Действия")
        
        # Таб 3: Лог и мониторинг
        self.log_tab = self._create_log_tab()
        self.tab_widget.addTab(self.log_tab, "📋 Лог")
        
        # Добавляем TabWidget
        layout.addWidget(self.tab_widget)
        
        # Изначально показываем GitHub группу
        self.on_deployment_mode_changed("GitHub")
    
    def _create_settings_tab(self):
        """Создание таба с настройками"""
        tab = QWidget()
        layout = QHBoxLayout()
        tab.setLayout(layout)
        
        # Левая панель: основные настройки
        left = QVBoxLayout()
        
        # Vault / Quartz / Repo
        paths_card = CardWidget()
        paths_layout = QFormLayout()
        paths_card.setLayout(paths_layout)
        
        self.vault_path = LineEdit()
        self.vault_path.setPlaceholderText("Выберите папку Obsidian Vault...")
        vault_btn = PrimaryPushButton("Выбрать Vault")
        vault_btn.clicked.connect(self.select_vault)
        vault_h = QHBoxLayout()
        vault_h.addWidget(self.vault_path)
        vault_h.addWidget(vault_btn)
        paths_layout.addRow(StrongBodyLabel("Obsidian Vault:"), vault_h)
        
        # Режим деплоя
        self.deployment_mode = ComboBox()
        self.deployment_mode.addItems(["GitHub", "Локальный"])
        self.deployment_mode.currentTextChanged.connect(self.on_deployment_mode_changed)
        paths_layout.addRow(StrongBodyLabel("Режим деплоя:"), self.deployment_mode)
        
        left.addWidget(paths_card)
        
        # GitHub настройки
        self.github_group = CardWidget()
        gh_layout = QFormLayout()
        self.github_group.setLayout(gh_layout)
        
        self.quartz_repo = LineEdit()
        self.quartz_repo.setText(DEFAULT_QUARTZ_REPO)
        gh_layout.addRow(StrongBodyLabel("Quartz repo URL:"), self.quartz_repo)
        
        self.deploy_branch = LineEdit()
        self.deploy_branch.setText(DEFAULT_DEPLOY_BRANCH)
        gh_layout.addRow(StrongBodyLabel("Ветка деплоя:"), self.deploy_branch)
        
        left.addWidget(self.github_group)
        
        # Локальные настройки
        self.local_group = CardWidget()
        local_layout = QFormLayout()
        self.local_group.setLayout(local_layout)
        
        self.quartz_path = LineEdit()
        self.quartz_path.setPlaceholderText("Путь к папке Quartz...")
        quartz_btn = PrimaryPushButton("Папка Quartz")
        quartz_btn.clicked.connect(self.select_quartz_folder)
        quartz_h = QHBoxLayout()
        quartz_h.addWidget(self.quartz_path)
        quartz_h.addWidget(quartz_btn)
        local_layout.addRow(StrongBodyLabel("Quartz root:"), quartz_h)
        
        # Информация о локальном режиме
        info_label = CaptionLabel("💡 Локальный режим: синхронизация контента без сборки")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        local_layout.addRow(info_label)
        
        left.addWidget(self.local_group)
        
        # Настройки сайта
        site_card = CardWidget()
        site_layout = QFormLayout()
        site_card.setLayout(site_layout)
        self.site_name = LineEdit()
        self.site_name.setText(DEFAULT_SITE_NAME)
        self.extra_settings = LineEdit()
        self.extra_settings.setText(DEFAULT_EXTRA_SETTINGS)
        site_layout.addRow(StrongBodyLabel("Имя сайта:"), self.site_name)
        site_layout.addRow(StrongBodyLabel("Доп. настройки:"), self.extra_settings)
        left.addWidget(site_card)
        

        
        left.addStretch()
        layout.addLayout(left, 2)
        
        # Правая панель: предпросмотр и информация
        right = QVBoxLayout()
        
        # Информационная карточка
        info_card = CardWidget()
        info_layout = QVBoxLayout()
        info_card.setLayout(info_layout)
        
        info_text = CaptionLabel("""
        <h3>Как использовать:</h3>
        <ol>
        <li>Выберите папку Obsidian Vault</li>
        <li>Выберите режим деплоя</li>
        <li>Настройте параметры</li>
        <li>Нажмите кнопки действий</li>
        </ol>
        
        <h3>Режимы:</h3>
        <ul>
        <li><b>GitHub:</b> Полный деплой через GitHub Pages</li>
        <li><b>Локальный:</b> Синхронизация контента</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        right.addWidget(info_card)
        right.addStretch()
        layout.addLayout(right, 1)
        
        return tab
    
    def _create_actions_tab(self):
        """Создание таба с действиями"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Заголовок
        actions_title = SubtitleLabel("Действия")
        actions_title.setStyleSheet("font-size: 18px; margin: 20px 0;")
        layout.addWidget(actions_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Карточки действий
        actions_layout = QHBoxLayout()
        
        # Карточка конвертации
        convert_card = CardWidget()
        convert_layout = QVBoxLayout()
        convert_card.setLayout(convert_layout)
        
        convert_desc = CaptionLabel("Преобразует Dataview блоки в статический Markdown")
        convert_layout.addWidget(convert_desc)
        
        self.btn_convert = PrimaryPushButton("Конвертировать Dataview")
        self.btn_convert.clicked.connect(self.on_convert_dataview)
        self.btn_convert.setMinimumHeight(50)
        convert_layout.addWidget(self.btn_convert)
        
        actions_layout.addWidget(convert_card)
        
        # Карточка настройки
        setup_card = CardWidget()
        setup_layout = QVBoxLayout()
        setup_card.setLayout(setup_layout)
        
        setup_desc = CaptionLabel("Настраивает Quartz для выбранного режима деплоя")
        setup_layout.addWidget(setup_desc)
        
        self.btn_setup = PrimaryPushButton("Настроить Quartz")
        self.btn_setup.clicked.connect(self.on_setup_quartz)
        self.btn_setup.setMinimumHeight(50)
        setup_layout.addWidget(self.btn_setup)
        
        actions_layout.addWidget(setup_card)
        
        # Карточка деплоя
        deploy_card = CardWidget()
        deploy_layout = QVBoxLayout()
        deploy_card.setLayout(deploy_layout)
        
        deploy_desc = CaptionLabel("Выполняет деплой контента в выбранном режиме")
        deploy_layout.addWidget(deploy_desc)
        
        self.btn_deploy = PrimaryPushButton("Деплой")
        self.btn_deploy.clicked.connect(self.on_deploy)
        self.btn_deploy.setMinimumHeight(50)
        deploy_layout.addWidget(self.btn_deploy)
        
        actions_layout.addWidget(deploy_card)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        return tab
    
    def _create_log_tab(self):
        """Создание таба с логом и мониторингом"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Заголовок
        log_title = SubtitleLabel("Лог и мониторинг")
        log_title.setStyleSheet("font-size: 18px; margin: 20px 0;")
        layout.addWidget(log_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Лог
        log_card = CardWidget()
        log_layout = QVBoxLayout()
        log_card.setLayout(log_layout)
        
        self.log_view = TextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(300)
        log_layout.addWidget(self.log_view)
        
        # Прогресс
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(StrongBodyLabel("Прогресс:"))
        
        self.progress = ProgressRing()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        progress_layout.addWidget(self.progress)
        progress_layout.addStretch()
        
        log_layout.addLayout(progress_layout)
        layout.addWidget(log_card)
        
        # Кнопки управления логом
        log_controls = QHBoxLayout()
        
        clear_btn = TransparentPushButton("Очистить лог")
        clear_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(clear_btn)
        
        save_btn = TransparentPushButton("Сохранить лог")
        save_btn.clicked.connect(self.save_log)
        log_controls.addWidget(save_btn)
        
        log_controls.addStretch()
        layout.addLayout(log_controls)
        
        return tab
    
    def _build_fallback_ui(self):
        """Fallback UI для случаев когда Fluent недоступен"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        # ---- Левая панель: настройки ----
        left = QVBoxLayout()

        # Vault / Quartz / Repo
        paths_group = QGroupBox("Пути и репозитории")
        pg_layout = QFormLayout()
        paths_group.setLayout(pg_layout)

        self.vault_path = QLineEdit()
        vault_btn = PushButton("Выбрать Vault")
        vault_btn.clicked.connect(self.select_vault)
        vault_h = QHBoxLayout()
        vault_h.addWidget(self.vault_path)
        vault_h.addWidget(vault_btn)
        pg_layout.addRow(BodyLabel("Obsidian Vault:"), vault_h)

        # Режим деплоя
        self.deployment_mode = ComboBox()
        self.deployment_mode.addItems(["GitHub", "Локальный"])
        self.deployment_mode.currentTextChanged.connect(self.on_deployment_mode_changed)
        pg_layout.addRow(BodyLabel("Режим деплоя:"), self.deployment_mode)

        # GitHub настройки
        self.github_group = QGroupBox("GitHub настройки")
        gh_layout = QFormLayout()
        self.github_group.setLayout(gh_layout)
        
        self.quartz_repo = QLineEdit(DEFAULT_QUARTZ_REPO)
        gh_layout.addRow(BodyLabel("Quartz repo URL:"), self.quartz_repo)
        
        self.deploy_branch = QLineEdit(DEFAULT_DEPLOY_BRANCH)
        gh_layout.addRow(BodyLabel("Ветка деплоя:"), self.deploy_branch)
        
        left.addWidget(self.github_group)

        # Локальные настройки
        self.local_group = QGroupBox("Локальные настройки (только синхронизация)")
        local_layout = QFormLayout()
        self.local_group.setLayout(local_layout)
        
        self.quartz_path = QLineEdit()
        quartz_btn = PushButton("Папка Quartz")
        quartz_btn.clicked.connect(self.select_quartz_folder)
        quartz_h = QHBoxLayout()
        quartz_h.addWidget(self.quartz_path)
        quartz_h.addWidget(quartz_btn)
        local_layout.addRow(BodyLabel("Quartz root:"), quartz_h)
        
        # Информация о локальном режиме
        info_label = CaptionLabel("💡 Локальный режим: синхронизация контента без сборки")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        local_layout.addRow(info_label)
        
        left.addWidget(self.local_group)

        left.addWidget(paths_group)

        # Настройки сайта
        site_group = QGroupBox("Настройки сайта")
        sg_layout = QFormLayout()
        site_group.setLayout(sg_layout)
        self.site_name = QLineEdit(DEFAULT_SITE_NAME)
        self.extra_settings = QLineEdit(DEFAULT_EXTRA_SETTINGS)
        sg_layout.addRow(BodyLabel("Имя сайта:"), self.site_name)
        sg_layout.addRow(BodyLabel("Доп. настройки:"), self.extra_settings)
        left.addWidget(site_group)

        # Кнопки действий
        actions_group = QGroupBox("Действия")
        a_layout = QVBoxLayout()
        actions_group.setLayout(a_layout)

        self.btn_convert = PushButton("Конвертировать Dataview")
        self.btn_convert.clicked.connect(self.on_convert_dataview)
        a_layout.addWidget(self.btn_convert)

        self.btn_setup = PushButton("Настроить Quartz")
        self.btn_setup.clicked.connect(self.on_setup_quartz)
        a_layout.addWidget(self.btn_setup)

        self.btn_deploy = PushButton("Деплой")
        self.btn_deploy.clicked.connect(self.on_deploy)
        a_layout.addWidget(self.btn_deploy)

        left.addWidget(actions_group)
        left.addStretch()
        layout.addLayout(left, 2)

        # ---- Правая панель: лог и прогресс ----
        right = QVBoxLayout()
        log_group = QGroupBox("Лог")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        log_layout.addWidget(self.progress)
        right.addWidget(log_group)
        layout.addLayout(right, 3)
        
        # Изначально показываем GitHub группу
        self.on_deployment_mode_changed("GitHub")

    # ---------- UI helpers ----------
    def append_log(self, text: str):
        if hasattr(self.log_view, 'appendPlainText'):
            self.log_view.appendPlainText(text)
        else:
            # Для TextEdit используем insertPlainText
            self.log_view.insertPlainText(text + '\n')

    def set_progress(self, value: int):
        self.progress.setValue(value)

    def select_vault(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите Obsidian Vault")
        if folder:
            self.vault_path.setText(folder)

    def select_quartz_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите корневую папку Quartz (или пусто, чтобы клонировать)")
        if folder:
            self.quartz_path.setText(folder)

    def _run_worker(self, target_fn, *args, **kwargs):
        # блокировка кнопок
        self.btn_convert.setEnabled(False)
        self.btn_setup.setEnabled(False)
        self.btn_deploy.setEnabled(False)

        worker = WorkerThread(target_fn, *args, **kwargs)
        worker.log.connect(self.append_log)
        worker.finished.connect(self._on_worker_finished)
        self.current_worker = worker
        worker.start()

    def _on_worker_finished(self, success: bool, message: str):
        self.append_log(f"[WORKER] Завершено: {'OK' if success else 'FAIL'} — {message}")
        self.btn_convert.setEnabled(True)
        self.btn_setup.setEnabled(True)
        self.btn_deploy.setEnabled(True)
        
        # Показываем уведомление
        if FLUENT_AVAILABLE and InfoBar:
            try:
                if success:
                    InfoBar.success(
                        title="✅ Успешно",
                        content=message,
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        title="❌ Ошибка",
                        content=message,
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
            except Exception as e:
                # Fallback если InfoBar недоступен
                print(f"InfoBar error: {e}")
        else:
            # Fallback для стандартных виджетов
            if success:
                QMessageBox.information(self, "Успешно", message)
            else:
                QMessageBox.critical(self, "Ошибка", message)

    # ---------- Событийные обработчики ----------
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
    
    def on_convert_dataview(self):
        vault = self.vault_path.text().strip()
        if not vault or not Path(vault).exists():
            if FLUENT_AVAILABLE and MessageBox:
                MessageBox.warning(self, "Ошибка", "Укажите корректную папку Vault.")
            else:
                QMessageBox.warning(self, "Ошибка", "Укажите корректную папку Vault.")
            return
        self.append_log("Запуск преобразования Dataview → Markdown...")
        # Запуск в отдельном потоке
        self._run_worker(convert_dataview_in_vault, vault, True)  # backup=True

    def on_setup_quartz(self):
        """Настройка Quartz в выбранном режиме"""
        # Обновляем конфигурацию из UI
        self._update_deployment_config()
        
        if not self._validate_setup_config():
            return
        
        self.append_log(f"Настройка Quartz в режиме: {self.deployment_config.mode.value}")
        self._run_worker(self._setup_quartz_flow)
    
    def _setup_quartz_flow(self, logger=None):
        """Поток настройки Quartz"""
        if logger is None:
            logger = print
        
        try:
            # Создаем менеджер деплоя
            manager = get_deployment_manager(self.deployment_config.mode.value)
            
            # Настраиваем Quartz
            result = manager.setup_quartz(self.deployment_config, logger=logger)
            
            if result.success:
                logger(f"Quartz настроен: {result.message}")
                return result.message
            else:
                raise RuntimeError(result.error or "Неизвестная ошибка настройки")
                
        except Exception as e:
            logger(f"Ошибка настройки Quartz: {e}")
            raise
    
    def on_deploy(self):
        """Деплой контента"""
        vault = self.vault_path.text().strip()
        if not vault or not Path(vault).exists():
            if FLUENT_AVAILABLE and MessageBox:
                MessageBox.warning(self, "Ошибка", "Укажите корректную папку Vault.")
            else:
                QMessageBox.warning(self, "Ошибка", "Укажите корректную папку Vault.")
            return
        
        # Обновляем конфигурацию из UI
        self._update_deployment_config()
        
        if not self._validate_deploy_config():
            return
        
        self.append_log(f"Запуск деплоя в режиме: {self.deployment_config.mode.value}")
        self._run_worker(self._deploy_flow, vault)
    
    def _deploy_flow(self, vault_path: str, logger=None):
        """Поток деплоя"""
        if logger is None:
            logger = print
        
        try:
            # Создаем менеджер деплоя
            manager = get_deployment_manager(self.deployment_config.mode.value)
            
            # Выполняем деплой
            result = manager.deploy(self.deployment_config, vault_path, logger=logger)
            
            if result.success:
                logger(f"Деплой завершен: {result.message}")
                if result.deployed_url:
                    logger(f"URL: {result.deployed_url}")
                return result.message
            else:
                raise RuntimeError(result.error or "Неизвестная ошибка деплоя")
                
        except Exception as e:
            logger(f"Ошибка деплоя: {e}")
            raise
    
    def _update_deployment_config(self):
        """Обновляет конфигурацию деплоя из UI"""
        self.deployment_config.site_name = self.site_name.text().strip()
        
        if self.deployment_config.mode == DeploymentMode.GITHUB:
            self.deployment_config.repo_url = self.quartz_repo.text().strip()
            self.deployment_config.deploy_branch = self.deploy_branch.text().strip()
        else:
            self.deployment_config.local_path = self.quartz_path.text().strip()
    
    def _validate_setup_config(self) -> bool:
        """Проверяет конфигурацию для настройки"""
        if self.deployment_config.mode == DeploymentMode.GITHUB:
            if not self.quartz_repo.text().strip():
                self._show_warning("Укажите URL репозитория Quartz.")
                return False
        else:
            if not self.quartz_path.text().strip():
                self._show_warning("Укажите путь к локальной установке Quartz.")
                return False
        
        return True
    
    def _validate_deploy_config(self) -> bool:
        """Проверяет конфигурацию для деплоя"""
        if not self._validate_setup_config():
            return False
        
        if self.deployment_config.mode == DeploymentMode.LOCAL:
            quartz_path = Path(self.deployment_config.local_path)
            if not quartz_path.exists():
                self._show_warning("Локальная папка Quartz не найдена.")
                return False
        
        return True
    
    def _show_warning(self, message: str):
        """Универсальный метод показа предупреждений"""
        if FLUENT_AVAILABLE and MessageBox:
            MessageBox.warning(self, "Ошибка", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def clear_log(self):
        """Очищает лог"""
        self.log_view.clear()
        self.append_log("Лог очищен")
    
    def save_log(self):
        """Сохраняет лог в файл"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить лог", "", "Text Files (*.txt);;All Files (*)"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_view.toPlainText())
                self.append_log(f"Лог сохранен в: {filename}")
        except Exception as e:
            self.append_log(f"Ошибка сохранения лога: {e}")
    


# ---------- Запуск ----------
def run_app():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
