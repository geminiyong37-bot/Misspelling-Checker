import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import verify_key


class VerifyKeyTests(unittest.TestCase):
    def test_rejected_key_is_reported_as_invalid_key(self):
        with patch.object(sys, "argv", ["verify_key.exe", "sk-test"]), patch.object(
            verify_key,
            "validate_api_key",
            return_value=(False, "유효하지 않은 API 키입니다."),
        ), patch("sys.stderr"):
            with self.assertRaises(SystemExit) as result:
                verify_key.main()

        self.assertEqual(result.exception.code, 2)

    def test_invalid_request_is_not_reported_as_invalid_key(self):
        for key, provider in (
            ("sk-test", "OpenAI"),
            ("gemini-test", "Gemini"),
            ("sk-ant-test", "Anthropic"),
        ):
            with self.subTest(provider=provider), patch.object(
                sys, "argv", ["verify_key.exe", key]
            ), patch.object(
                verify_key,
                "validate_api_key",
                return_value=(False, f"연결 오류: {provider} request failed (400): invalid_request_error"),
            ), patch("sys.stderr"):
                with self.assertRaises(SystemExit) as result:
                    verify_key.main()
                self.assertEqual(result.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
