import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import rag_context


class RagContextTests(unittest.TestCase):
    def test_no_selected_mode_returns_no_rag_prompt(self):
        self.assertEqual(rag_context.build_rag_prompt_section({}), "")

    def test_date_mode_contains_only_date_time_and_number_sections(self):
        prompt = rag_context.build_rag_prompt_section({"check_date_format": True})

        self.assertIn("1. 연월일 및 날짜 표기", prompt)
        self.assertIn("2. 시간 표기", prompt)
        self.assertIn("3. 숫자 표기", prompt)
        self.assertNotIn("7. 순화어", prompt)
        self.assertNotIn("8. 번역투", prompt)

    def test_plain_language_and_style_modes_are_separate(self):
        plain = rag_context.build_rag_prompt_section({"suggest_plain_language": True})
        style = rag_context.build_rag_prompt_section({"improve_style": True})

        self.assertIn("7. 순화어", plain)
        self.assertNotIn("8. 번역투", plain)
        self.assertIn("8. 번역투", style)
        self.assertNotIn("7. 순화어", style)


if __name__ == "__main__":
    unittest.main()
