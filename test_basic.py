#!/usr/bin/env python3
"""
Простой тест базовой функциональности без GUI
"""

def test_dataview_converter():
    """Тест импорта dataview_converter"""
    try:
        from dataview_converter import convert_dataview_in_vault
        print("✓ dataview_converter импортирован успешно")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта dataview_converter: {e}")
        return False

def test_deployment_manager():
    """Тест импорта deployment_manager"""
    try:
        from deployment_manager import DeploymentMode, get_deployment_manager
        print("✓ deployment_manager импортирован успешно")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта deployment_manager: {e}")
        return False

def test_git_utils():
    """Тест импорта git_utils"""
    try:
        from git_utils import git_clone
        print("✓ git_utils импортирован успешно")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта git_utils: {e}")
        return False

def test_utils():
    """Тест импорта utils"""
    try:
        from utils import ensure_dir
        print("✓ utils импортирован успешно")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта utils: {e}")
        return False

def main():
    print("Тестирование базовой функциональности...")
    print("=" * 50)
    
    tests = [
        test_dataview_converter,
        test_deployment_manager,
        test_git_utils,
        test_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Результат: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("✓ Все базовые модули работают корректно!")
        print("\nДля запуска GUI приложения выполните:")
        print("python main.py")
    else:
        print("✗ Некоторые модули не работают")
        print("Установите зависимости: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
