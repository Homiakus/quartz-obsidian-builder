# test_deployment_manager.py
import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch

from deployment_manager import (
    DeploymentMode, QuartzConfig, DeploymentManager,
    GitHubDeploymentManager, LocalDeploymentManager,
    DeploymentManagerFactory, get_deployment_manager
)


class TestDeploymentMode(unittest.TestCase):
    """Тесты для enum DeploymentMode"""
    
    def test_deployment_mode_values(self):
        """Проверка значений enum"""
        self.assertEqual(DeploymentMode.GITHUB.value, "github")
        self.assertEqual(DeploymentMode.LOCAL.value, "local")


class TestQuartzConfig(unittest.TestCase):
    """Тесты для конфигурации Quartz"""
    
    def test_default_config(self):
        """Проверка значений по умолчанию"""
        config = QuartzConfig(mode=DeploymentMode.GITHUB)
        self.assertEqual(config.mode, DeploymentMode.GITHUB)
        self.assertEqual(config.repo_url, "https://github.com/jackyzha0/quartz.git")
        self.assertEqual(config.branch, "main")
        self.assertEqual(config.deploy_branch, "gh-pages")
        self.assertEqual(config.site_name, "Мой сайт")
    
    def test_custom_config(self):
        """Проверка пользовательской конфигурации"""
        config = QuartzConfig(
            mode=DeploymentMode.LOCAL,
            local_path="/custom/path",
            site_name="Мой блог"
        )
        self.assertEqual(config.mode, DeploymentMode.LOCAL)
        self.assertEqual(config.local_path, "/custom/path")
        self.assertEqual(config.site_name, "Мой блог")


class TestDeploymentManagerFactory(unittest.TestCase):
    """Тесты для фабрики менеджеров деплоя"""
    
    def test_create_github_manager(self):
        """Создание GitHub менеджера"""
        manager = DeploymentManagerFactory.create_manager(DeploymentMode.GITHUB)
        self.assertIsInstance(manager, GitHubDeploymentManager)
    
    def test_create_local_manager(self):
        """Создание локального менеджера"""
        manager = DeploymentManagerFactory.create_manager(DeploymentMode.LOCAL)
        self.assertIsInstance(manager, LocalDeploymentManager)
    
    def test_invalid_mode(self):
        """Проверка ошибки при неверном режиме"""
        with self.assertRaises(ValueError):
            DeploymentManagerFactory.create_manager("invalid")


class TestGetDeploymentManager(unittest.TestCase):
    """Тесты для функции get_deployment_manager"""
    
    def test_get_github_manager(self):
        """Получение GitHub менеджера по строке"""
        manager = get_deployment_manager("github")
        self.assertIsInstance(manager, GitHubDeploymentManager)
    
    def test_get_local_manager(self):
        """Получение локального менеджера по строке"""
        manager = get_deployment_manager("local")
        self.assertIsInstance(manager, LocalDeploymentManager)
    
    def test_case_insensitive(self):
        """Проверка нечувствительности к регистру"""
        manager = get_deployment_manager("GITHUB")
        self.assertIsInstance(manager, GitHubDeploymentManager)
    
    def test_invalid_mode_string(self):
        """Проверка ошибки при неверной строке режима"""
        with self.assertRaises(ValueError):
            get_deployment_manager("invalid_mode")


class TestGitHubDeploymentManager(unittest.TestCase):
    """Тесты для GitHub менеджера деплоя"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = QuartzConfig(
            mode=DeploymentMode.GITHUB,
            repo_url="https://github.com/test/quartz.git"
        )
        self.manager = GitHubDeploymentManager()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    @patch('deployment_manager.ensure_quartz_cloned_and_setup')
    def test_setup_quartz_success(self, mock_setup):
        """Успешная настройка Quartz"""
        mock_setup.return_value = "Quartz готов"
        
        # Создаем mock package.json
        quartz_path = Path(self.temp_dir) / "quartz_github"
        quartz_path.mkdir()
        (quartz_path / "package.json").write_text('{"name": "quartz"}')
        
        self.config.local_path = str(quartz_path)
        
        result = self.manager.setup_quartz(self.config, logger=print)
        
        self.assertTrue(result.success)
        self.assertIn("GitHub деплоя", result.message)
        self.assertEqual(result.quartz_path, str(quartz_path))
    
    @patch('deployment_manager.ensure_quartz_cloned_and_setup')
    def test_setup_quartz_failure(self, mock_setup):
        """Ошибка настройки Quartz"""
        mock_setup.side_effect = RuntimeError("Clone failed")
        
        result = self.manager.setup_quartz(self.config, logger=print)
        
        self.assertFalse(result.success)
        self.assertIn("Ошибка настройки", result.message)
        self.assertIn("Clone failed", result.error)


class TestLocalDeploymentManager(unittest.TestCase):
    """Тесты для локального менеджера деплоя"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = QuartzConfig(
            mode=DeploymentMode.LOCAL,
            local_path=self.temp_dir
        )
        self.manager = LocalDeploymentManager()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_quartz_success(self):
        """Успешная проверка локальной установки"""
        # Создаем mock package.json
        (Path(self.temp_dir) / "package.json").write_text('{"name": "quartz"}')
        
        result = self.manager.setup_quartz(self.config, logger=print)
        
        self.assertTrue(result.success)
        self.assertIn("Локальная установка", result.message)
    
    def test_setup_quartz_missing_package_json(self):
        """Ошибка при отсутствии package.json"""
        result = self.manager.setup_quartz(self.config, logger=print)
        
        self.assertFalse(result.success)
        self.assertIn("не содержит Quartz", result.error)
    
    def test_setup_quartz_missing_path(self):
        """Ошибка при отсутствии пути"""
        self.config.local_path = "/nonexistent/path"
        
        result = self.manager.setup_quartz(self.config, logger=print)
        
        self.assertFalse(result.success)
        self.assertIn("не найдена", result.error)


if __name__ == "__main__":
    unittest.main()
