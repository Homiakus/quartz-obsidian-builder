# test_dataview_converter.py
import unittest
from pathlib import Path
import tempfile
import shutil

from dataview_converter import convert_dataview_in_vault

class TestDataviewConverter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"
        self.vault_path.mkdir()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_simple_table_conversion(self):
        # Создаем тестовый файл с dataview блоком
        test_file = self.vault_path / "test.md"
        test_content = """# Test
        
```dataview
TABLE title, tags FROM "."
```

Some content."""
        
        test_file.write_text(test_content, encoding="utf-8")
        
        # Запускаем конвертацию
        result = convert_dataview_in_vault(str(self.vault_path), backup=False, logger=lambda x: None)
        
        # Проверяем результат
        self.assertIn("Конвертация Dataview завершена", result)
        
        # Проверяем что файл был изменен
        new_content = test_file.read_text(encoding="utf-8")
        self.assertNotIn("```dataview", new_content)
        self.assertIn("| title | tags |", new_content)

if __name__ == "__main__":
    unittest.main()
