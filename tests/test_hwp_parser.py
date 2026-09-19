import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import hwp_parser


class KordocPathTests(unittest.TestCase):
    def test_environment_override_uses_cli_cjs(self):
        self.assertTrue(hasattr(hwp_parser, "get_kordoc_path"))

        with patch.dict(os.environ, {"KORDOC_HOME": r"D:\tools\kordoc"}):
            path = hwp_parser.get_kordoc_path()

        self.assertEqual(path, os.path.join(r"D:\tools\kordoc", "dist", "cli.cjs"))

    def test_default_development_path_uses_archive_kordoc(self):
        self.assertTrue(hasattr(hwp_parser, "get_kordoc_path"))

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("KORDOC_HOME", None)
            path = Path(hwp_parser.get_kordoc_path())

        self.assertEqual(path.name, "cli.cjs")
        self.assertEqual(path.parent.parent.name, "kordoc")
        self.assertEqual(path.parent.parent.parent.name, "Archive")


if __name__ == "__main__":
    unittest.main()
