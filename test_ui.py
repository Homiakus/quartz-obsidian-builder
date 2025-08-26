"""
@file: test_ui.py
@description: Простой тест UI функциональности
@dependencies: PyQt6
@created: 2024-12-19
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class TestWindow(QMainWindow):
    """Простое тестовое окно для проверки PyQt6"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест PyQt6")
        self.resize(400, 300)
        
        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Заголовок
        title = QLabel("PyQt6 работает!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; margin: 20px;")
        layout.addWidget(title)
        
        # Тестовая кнопка
        test_btn = QPushButton("Нажми меня!")
        test_btn.clicked.connect(self.on_button_click)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        layout.addWidget(test_btn)
        
        # Статус
        self.status_label = QLabel("Готов к тестированию")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Темная тема
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: white;
            }
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
    
    def on_button_click(self):
        """Обработчик клика по кнопке"""
        self.status_label.setText("Кнопка работает! ✅")
        print("✅ PyQt6 работает корректно!")

def test_pyqt6():
    """Тест PyQt6"""
    try:
        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        print("🚀 PyQt6 тест запущен успешно!")
        return app.exec()
    except Exception as e:
        print(f"❌ Ошибка PyQt6: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_pyqt6())
