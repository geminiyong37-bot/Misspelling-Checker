import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QApplication, QDialog
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


class StartupFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt_app = QApplication.instance() or QApplication([])

    def test_drop_area_show_event_does_not_open_startup_dialogs(self):
        window = app.MainWindow()
        try:
            with patch.object(app.WelcomeDialog, "exec") as welcome_exec, patch.object(
                app.QTimer, "singleShot"
            ) as single_shot:
                window.drop_area.showEvent(QShowEvent())

            welcome_exec.assert_not_called()
            single_shot.assert_not_called()
        finally:
            window.close()

    def test_main_window_schedules_initial_setup_once_after_show(self):
        window = app.MainWindow()
        try:
            with patch.object(app.QTimer, "singleShot") as single_shot:
                window.showEvent(QShowEvent())
                window.showEvent(QShowEvent())

            single_shot.assert_called_once()
            delay, callback = single_shot.call_args.args
            self.assertEqual(delay, 0)
            self.assertIs(callback.__self__, window)
            self.assertEqual(callback.__name__, "_initial_setup")
        finally:
            window.close()

    def test_initial_setup_handles_welcome_then_checks_api_key(self):
        window = app.MainWindow()
        config = {"provider": app.PROVIDER_GEMINI, "keys": {}, "show_welcome": True}
        try:
            with patch.object(app, "_load_config", return_value=config), patch.object(
                app.WelcomeDialog,
                "exec",
                return_value=QDialog.DialogCode.Accepted,
            ) as welcome_exec, patch.object(
                window, "_ensure_api_key"
            ) as ensure_api_key:
                window._initial_setup()

            welcome_exec.assert_called_once()
            ensure_api_key.assert_called_once()
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
