import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ai_result_utils import ai_errors_to_rows
from excel_exporter import create_workbook


class ResultContextTests(unittest.TestCase):
    def test_excel_shows_one_word_on_each_side_of_typo(self):
        rows = [{
            "file": "sample.hwp",
            "page": 1,
            "sentence": "오늘 자료를 검토됬다 다시 제출합니다.",
            "original": "됬",
            "corrected": "됐",
            "reason": "맞춤법",
        }]

        sheet = create_workbook(rows).active

        self.assertEqual(sheet.cell(2, 2).value, "자료를 검토됬다 다시")
        self.assertEqual(sheet.cell(2, 3).value, "자료를 검토됐다 다시")

    def test_same_typo_in_different_contexts_keeps_both_rows(self):
        rows = [
            {"file": "sample.hwp", "sentence": "가장 좋은 됬다 결과", "original": "됬", "corrected": "됐", "reason": "맞춤법"},
            {"file": "sample.hwp", "sentence": "다시 확인 됬다 내용", "original": "됬", "corrected": "됐", "reason": "맞춤법"},
        ]

        sheet = create_workbook(rows).active

        self.assertEqual(sheet.max_row, 3)

    def test_cli_rows_keep_sentence_for_context(self):
        result = {"errors": [{"sentence": "오늘 자료를 검토됬다 다시", "original": "됬", "corrected": "됐"}]}

        self.assertEqual(ai_errors_to_rows(result)[0]["sentence"], result["errors"][0]["sentence"])


if __name__ == "__main__":
    unittest.main()
