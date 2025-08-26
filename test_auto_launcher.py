"""
@file: test_auto_launcher.py
@description: Тесты для модуля автозапуска
@dependencies: auto_launcher, local_server
@created: 2024-12-19
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import os

# Импортируем тестируемые модули
try:
    from auto_launcher import create_auto_launcher, AutoLauncher
    from local_server import create_local_server, LocalQuartzServer
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Модули недоступны для тестирования: {e}")
    MODULES_AVAILABLE = False


@unittest.skipUnless(MODULES_AVAILABLE, "Модули автозапуска недоступны")
class TestAutoLauncher(unittest.TestCase):
    """Тесты для модуля автозапуска"""
    
    def setUp(self):
        """Подготовка тестовой среды"""
        # Создаем временные папки
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "vault"
        self.quartz_path = Path(self.temp_dir) / "quartz"
        
        # Создаем структуру папок
        self.vault_path.mkdir()
        self.quartz_path.mkdir()
        
        # Создаем тестовые файлы
        (self.vault_path / "test.md").write_text("# Test")
        (self.quartz_path / "package.json").write_text('{"scripts": {"start": "echo test"}}')
    
    def tearDown(self):
        """Очистка после тестов"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_auto_launcher(self):
        """Тест создания AutoLauncher"""
        launcher = create_auto_launcher(str(self.vault_path), str(self.quartz_path))
        
        self.assertIsInstance(launcher, AutoLauncher)
        self.assertEqual(launcher.vault_path, self.vault_path)
        self.assertEqual(launcher.quartz_path, self.quartz_path)
    
    def test_auto_launcher_initialization(self):
        """Тест инициализации AutoLauncher"""
        launcher = AutoLauncher(str(self.vault_path), str(self.quartz_path))
        
        self.assertFalse(launcher.is_watching)
        self.assertIsNone(launcher.observer)
        self.assertIsNone(launcher.watcher)
        self.assertIsNone(launcher.local_server)
    
    @patch('auto_launcher.Observer')
    def test_start_watching(self, mock_observer):
        """Тест запуска отслеживания"""
        launcher = create_auto_launcher(str(self.vault_path), str(self.quartz_path))
        
        # Мокаем Observer
        mock_observer_instance = Mock()
        mock_observer.return_value = mock_observer_instance
        
        launcher.start_watching()
        
        self.assertTrue(launcher.is_watching)
        mock_observer_instance.schedule.assert_called_once()
        mock_observer_instance.start.assert_called_once()
    
    def test_stop_watching(self):
        """Тест остановки отслеживания"""
        launcher = create_auto_launcher(str(self.vault_path), str(self.quartz_path))
        
        # Запускаем отслеживание
        with patch('auto_launcher.Observer') as mock_observer:
            mock_observer_instance = Mock()
            mock_observer.return_value = mock_observer_instance
            launcher.start_watching()
        
        # Останавливаем
        launcher.stop_watching()
        
        self.assertFalse(launcher.is_watching)
    
    def test_context_manager(self):
        """Тест контекстного менеджера"""
        with create_auto_launcher(str(self.vault_path), str(self.quartz_path)) as launcher:
            self.assertIsInstance(launcher, AutoLauncher)
            self.assertTrue(hasattr(launcher, 'vault_path'))
            self.assertTrue(hasattr(launcher, 'quartz_path'))


@unittest.skipUnless(MODULES_AVAILABLE, "Модули локального сервера недоступны")
class TestLocalServer(unittest.TestCase):
    """Тесты для локального сервера"""
    
    def setUp(self):
        """Подготовка тестовой среды"""
        self.temp_dir = tempfile.mkdtemp()
        self.quartz_path = Path(self.temp_dir) / "quartz"
        self.quartz_path.mkdir()
        
        # Создаем package.json
        (self.quartz_path / "package.json").write_text('{"scripts": {"start": "echo test"}}')
    
    def tearDown(self):
        """Очистка после тестов"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_local_server(self):
        """Тест создания локального сервера"""
        server = create_local_server(str(self.quartz_path), 1313)
        
        self.assertIsInstance(server, LocalQuartzServer)
        self.assertEqual(server.quartz_path, self.quartz_path)
        self.assertEqual(server.port, 1313)
    
    def test_local_server_initialization(self):
        """Тест инициализации LocalQuartzServer"""
        server = LocalQuartzServer(str(self.quartz_path), 1313)
        
        self.assertFalse(server.is_running)
        self.assertIsNone(server.server)
        self.assertIsNone(server.server_thread)
        self.assertIsNone(server.process)
    
    @patch('local_server.run_quartz_build')
    def test_build_site(self, mock_build):
        """Тест сборки сайта"""
        server = create_local_server(str(self.quartz_path), 1313)
        
        server._build_site()
        
        mock_build.assert_called_once_with(str(self.quartz_path))
    
    def test_get_status(self):
        """Тест получения статуса сервера"""
        server = create_local_server(str(self.quartz_path), 1313)
        
        status = server.get_status()
        
        expected_keys = ['is_running', 'port', 'quartz_path', 'has_npm', 'has_http']
        for key in expected_keys:
            self.assertIn(key, status)
        
        self.assertFalse(status['is_running'])
        self.assertEqual(status['port'], 1313)
        self.assertEqual(status['quartz_path'], str(self.quartz_path))
        self.assertFalse(status['has_npm'])
        self.assertFalse(status['has_http'])
    
    def test_context_manager(self):
        """Тест контекстного менеджера"""
        with create_local_server(str(self.quartz_path), 1313) as server:
            self.assertIsInstance(server, LocalQuartzServer)
            self.assertTrue(hasattr(server, 'quartz_path'))
            self.assertTrue(hasattr(server, 'port'))


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_modules_import(self):
        """Тест импорта всех модулей"""
        try:
            import auto_launcher
            import local_server
            import modern_ui
            self.assertTrue(True, "Все модули успешно импортированы")
        except ImportError as e:
            self.fail(f"Ошибка импорта модуля: {e}")
    
    def test_dependencies_available(self):
        """Тест доступности зависимостей"""
        try:
            import PyQt6
            import watchdog
            self.assertTrue(True, "Основные зависимости доступны")
        except ImportError as e:
            self.fail(f"Отсутствует зависимость: {e}")


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)
