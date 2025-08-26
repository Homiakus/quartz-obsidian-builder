# main.py
"""
@file: main.py
@description: Главный файл приложения с поддержкой современного UI и автозапуска
@dependencies: modern_ui, gui, auto_launcher
@created: 2024-12-19
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Проверяет доступность зависимостей"""
    missing_deps = []

    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")

    try:
        import qfluentwidgets
    except ImportError:
        # PyQt-Fluent-Widgets не обязателен для simple режима
        pass

    try:
        import watchdog
    except ImportError:
        missing_deps.append("watchdog")

    if missing_deps:
        print("❌ Отсутствуют зависимости:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nУстановите зависимости:")
        print("pip install PyQt6 PyQt-Fluent-Widgets watchdog")
        return False

    return True

def main():
    """Главная функция приложения"""
    print("🚀 Запуск Quartz ← Obsidian Builder")

    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)

    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "modern":
            print("🎨 Запуск современного UI...")
            try:
                from modern_ui import run_modern_app
                run_modern_app()
                return
            except ImportError as e:
                print(f"❌ Ошибка импорта modern_ui: {e}")
                print("Пробуем упрощенную версию...")
                try:
                    from simple_modern_ui import run_simple_modern_app
                    run_simple_modern_app()
                    return
                except ImportError as e2:
                    print(f"❌ Ошибка импорта simple_modern_ui: {e2}")
                    print("Запускаем классический UI...")

        elif mode == "simple":
            print("🎨 Запуск упрощенного современного UI...")
            try:
                from simple_modern_ui import run_simple_modern_app
                run_simple_modern_app()
                return
            except ImportError as e:
                print(f"❌ Ошибка импорта simple_modern_ui: {e}")
                print("Запускаем классический UI...")

        elif mode == "classic":
            print("🔧 Запуск классического UI...")
            try:
                from gui import run_app
                run_app()
                return
            except ImportError as e:
                print(f"❌ Ошибка импорта gui: {e}")
                sys.exit(1)

        elif mode == "help":
            print("""
Quartz ← Obsidian Builder

Использование:
  python main.py [режим]

Режимы:
  modern  - Современный UI с Fluent Widgets (по умолчанию)
  simple  - Упрощенный современный UI (гарантированно работает)
  classic - Классический UI с табами
  help    - Показать эту справку

Примеры:
  python main.py modern   # Запуск современного UI
  python main.py simple   # Запуск упрощенного UI
  python main.py classic  # Запуск классического UI
            """)
            return

        else:
            print(f"❌ Неизвестный режим: {mode}")
            print("Используйте 'help' для справки")
            sys.exit(1)

    # По умолчанию пробуем современный UI, затем упрощенный
    print("🎨 Запуск современного UI (по умолчанию)...")
    try:
        from modern_ui import run_modern_app
        run_modern_app()
    except ImportError as e:
        print(f"❌ Ошибка импорта modern_ui: {e}")
        print("Пробуем упрощенную версию...")
        
        try:
            from simple_modern_ui import run_simple_modern_app
            run_simple_modern_app()
        except ImportError as e2:
            print(f"❌ Ошибка импорта simple_modern_ui: {e2}")
            print("Пробуем запустить классический UI...")

            try:
                from gui import run_app
                run_app()
            except ImportError as e3:
                print(f"❌ Критическая ошибка: {e3}")
                sys.exit(1)

if __name__ == "__main__":
    main()
