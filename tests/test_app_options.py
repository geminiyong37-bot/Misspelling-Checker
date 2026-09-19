import os
import sys
import unittest
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from PyQt6.QtWidgets import QApplication
import app


class ReviewOptionsUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QApplication.instance() or QApplication([])

    def test_all_optional_modes_are_unchecked_by_default(self):
        window = app.MainWindow()
        try:
            self.assertEqual(
                window.get_review_options(),
                {
                    "check_date_format": False,
                    "suggest_plain_language": False,
                    "improve_style": False,
                },
            )
            self.assertIn("날짜", window.cb_date_format.text())
            self.assertIn("순화어", window.cb_plain_language.text())
            self.assertIn("문체", window.cb_style.text())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
