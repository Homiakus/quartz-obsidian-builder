# deployment_manager.py
"""
Модуль управления режимами деплоя Quartz
Поддерживает GitHub и локальный режимы
"""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

from quartz import ensure_quartz_cloned_and_setup, copy_vault_to_quartz_content, run_quartz_build
from git_utils import git_clone, git_pull, git_commit_and_push


class DeploymentMode(Enum):
    """Режимы деплоя Quartz"""
    GITHUB = "github"
    LOCAL = "local"


@dataclass
class QuartzConfig:
    """Конфигурация для настройки Quartz"""
    mode: DeploymentMode
    repo_url: str = "https://github.com/jackyzha0/quartz.git"
    local_path: Optional[str] = None
    branch: str = "main"
    deploy_branch: str = "gh-pages"
    site_name: str = "Мой сайт"


@dataclass
class SetupResult:
    """Результат настройки Quartz"""
    success: bool
    message: str
    quartz_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class DeployResult:
    """Результат деплоя"""
    success: bool
    message: str
    deployed_url: Optional[str] = None
    error: Optional[str] = None


class DeploymentManager(ABC):
    """Абстрактный базовый класс для менеджеров деплоя"""
    
    @abstractmethod
    def setup_quartz(self, config: QuartzConfig, logger=print) -> SetupResult:
        """Настройка Quartz для деплоя"""
        pass
    
    @abstractmethod
    def deploy(self, config: QuartzConfig, vault_path: str, logger=print) -> DeployResult:
        """Деплой контента"""
        pass


class GitHubDeploymentManager(DeploymentManager):
    """Менеджер деплоя через GitHub"""
    
    def setup_quartz(self, config: QuartzConfig, logger=print) -> SetupResult:
        """Настройка Quartz через GitHub клонирование"""
        try:
            if not config.local_path:
                # Автоматически создаем папку для клонирования
                config.local_path = str(Path.cwd() / "quartz_github")
            
            quartz_path = Path(config.local_path)
            
            logger(f"Настройка Quartz в GitHub режиме: {config.repo_url}")
            logger(f"Локальная папка: {config.local_path}")
            
            # Клонируем или обновляем репозиторий
            ensure_quartz_cloned_and_setup(
                config.repo_url, 
                config.local_path, 
                logger=logger
            )
            
            # Проверяем что папка существует и содержит Quartz
            if not (quartz_path / "package.json").exists():
                raise RuntimeError("Quartz не был корректно клонирован")
            
            logger("Quartz успешно настроен для GitHub деплоя")
            
            return SetupResult(
                success=True,
                message="Quartz настроен для GitHub деплоя",
                quartz_path=config.local_path
            )
            
        except Exception as e:
            error_msg = f"Ошибка настройки GitHub режима: {e}"
            logger(error_msg)
            return SetupResult(
                success=False,
                message="Ошибка настройки",
                error=str(e)
            )
    
    def deploy(self, config: QuartzConfig, vault_path: str, logger=print) -> DeployResult:
        """Деплой через GitHub Pages"""
        try:
            if not config.local_path:
                raise ValueError("Не указан путь к Quartz")
            
            logger("Начинаем деплой через GitHub...")
            
            # 1. Синхронизируем контент
            logger("Синхронизация контента из Vault...")
            copy_vault_to_quartz_content(vault_path, config.local_path, logger=logger)
            
            # 2. Собираем сайт
            logger("Сборка сайта...")
            run_quartz_build(config.local_path, logger=logger)
            
            # 3. Коммитим и пушим изменения
            logger(f"Коммит и push в ветку {config.deploy_branch}...")
            commit_message = f"Auto deploy: {config.site_name} - {Path(vault_path).name}"
            
            git_commit_and_push(
                config.local_path,
                config.deploy_branch,
                commit_message
            )
            
            # 4. Формируем URL для GitHub Pages
            # Предполагаем что репозиторий на GitHub
            repo_name = config.repo_url.split("/")[-1].replace(".git", "")
            deployed_url = f"https://{repo_name}.github.io"
            
            logger(f"Деплой завершен успешно: {deployed_url}")
            
            return DeployResult(
                success=True,
                message="Деплой через GitHub завершен",
                deployed_url=deployed_url
            )
            
        except Exception as e:
            error_msg = f"Ошибка деплоя через GitHub: {e}"
            logger(error_msg)
            return DeployResult(
                success=False,
                message="Ошибка деплоя",
                error=str(e)
            )


class LocalDeploymentManager(DeploymentManager):
    """Менеджер локального деплоя Quartz (только синхронизация контента)"""
    
    def setup_quartz(self, config: QuartzConfig, logger=print) -> SetupResult:
        """Проверка существующей локальной установки Quartz"""
        try:
            if not config.local_path:
                raise ValueError("Для локального режима необходимо указать путь к Quartz")
            
            quartz_path = Path(config.local_path)
            
            logger(f"Проверка локальной установки Quartz: {config.local_path}")
            
            # Проверяем что папка существует и содержит Quartz
            if not quartz_path.exists():
                raise RuntimeError(f"Папка Quartz не найдена: {config.local_path}")
            
            if not (quartz_path / "package.json").exists():
                raise RuntimeError(f"Папка не содержит Quartz: {config.local_path}")
            
            # Проверяем что это git репозиторий
            if not (quartz_path / ".git").exists():
                logger("Предупреждение: папка не является git репозиторием")
            
            logger("Локальная установка Quartz проверена")
            
            return SetupResult(
                success=True,
                message="Локальная установка Quartz готова",
                quartz_path=config.local_path
            )
            
        except Exception as e:
            error_msg = f"Ошибка проверки локальной установки: {e}"
            logger(error_msg)
            return SetupResult(
                success=False,
                message="Ошибка проверки локальной установки",
                error=str(e)
            )
    
    def deploy(self, config: QuartzConfig, vault_path: str, logger=print) -> DeployResult:
        """Локальный деплой (только синхронизация контента, без сборки)"""
        try:
            if not config.local_path:
                raise ValueError("Не указан путь к Quartz")
            
            logger("Начинаем локальную синхронизацию контента...")
            
            # 1. Синхронизируем контент
            logger("Синхронизация контента из Vault...")
            copy_vault_to_quartz_content(vault_path, config.local_path, logger=logger)
            
            # 2. Формируем путь к контенту
            content_path = Path(config.local_path) / "content"
            if content_path.exists():
                deployed_url = f"file://{content_path.absolute()}"
                logger(f"Локальная синхронизация завершена: {deployed_url}")
                logger("💡 Для сборки сайта используйте команду 'npx quartz build' в папке Quartz")
                
                return DeployResult(
                    success=True,
                    message="Локальная синхронизация завершена",
                    deployed_url=deployed_url
                )
            else:
                raise RuntimeError("Папка content не найдена после синхронизации")
                
        except Exception as e:
            error_msg = f"Ошибка локальной синхронизации: {e}"
            logger(error_msg)
            
            return DeployResult(
                success=False,
                message="Ошибка локальной синхронизации",
                error=str(e)
            )


class DeploymentManagerFactory:
    """Фабрика для создания менеджеров деплоя"""
    
    @staticmethod
    def create_manager(mode: DeploymentMode) -> DeploymentManager:
        """Создает соответствующий менеджер деплоя"""
        if mode == DeploymentMode.GITHUB:
            return GitHubDeploymentManager()
        elif mode == DeploymentMode.LOCAL:
            return LocalDeploymentManager()
        else:
            raise ValueError(f"Неизвестный режим деплоя: {mode}")


def get_deployment_manager(mode: str) -> DeploymentManager:
    """Удобная функция для создания менеджера деплоя по строке"""
    try:
        deployment_mode = DeploymentMode(mode.lower())
        return DeploymentManagerFactory.create_manager(deployment_mode)
    except ValueError:
        raise ValueError(f"Поддерживаемые режимы: {[m.value for m in DeploymentMode]}")
