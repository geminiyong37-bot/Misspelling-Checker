import unittest
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class BuildConfigurationTests(unittest.TestCase):
    def test_installer_api_key_page_lists_provider_models(self):
        script = (PROJECT_ROOT / "installer.iss").read_text(encoding="utf-8")

        self.assertIn("Gemini: gemini-3.8-flash", script)
        self.assertIn("OpenAI: gpt-5.6-terra", script)
        self.assertIn("Anthropic: claude-haiku-4-5-20251001", script)

    def test_installer_is_compiled_in_staging_before_publish(self):
        script = (PROJECT_ROOT / "build.bat").read_text(encoding="utf-8")

        self.assertIn('set INSTALLER_OUTPUT=%STAGING%\\installer', script)
        self.assertIn('%ISCC% /O"%INSTALLER_OUTPUT%"', script)
        self.assertIn(
            'copy /y "%INSTALLER_OUTPUT%\\AI_Word_Speller_Setup.exe" '
            '"%SCRIPT_DIR%Output\\AI_Word_Speller_Setup.exe"',
            script,
        )

    def test_windows_build_script_uses_crlf_line_endings(self):
        content = (PROJECT_ROOT / "build.bat").read_bytes()

        self.assertIsNone(re.search(rb"(?<!\r)\n", content))


if __name__ == "__main__":
    unittest.main()
