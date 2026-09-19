import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from PyQt6.QtWidgets import QApplication
import app


class ApiKeyModelTextTests(unittest.TestCase):
    def test_api_key_prompt_lists_all_default_models(self):
        text = app.build_api_key_prompt_text()
        self.assertIn("Gemini: gemini-3.8-flash", text)
        self.assertIn("OpenAI: gpt-5.6-terra", text)
        self.assertIn("Anthropic: claude-haiku-4-5-20251001", text)

    def test_confirmation_uses_environment_override(self):
        with patch.dict(os.environ, {"TYPO_OPENAI_MODEL": "custom-openai"}):
            text = app.build_api_key_confirmation_text(app.PROVIDER_OPENAI)
        self.assertIn("공급자: openai", text)
        self.assertIn("모델: custom-openai", text)


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
