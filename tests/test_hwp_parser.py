import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import hwp_parser


class KordocPathTests(unittest.TestCase):
    def test_environment_override_uses_bundled_cli_name(self):
        self.assertTrue(hasattr(hwp_parser, "get_kordoc_path"))

        with patch.dict(os.environ, {"KORDOC_HOME": r"D:\tools\kordoc"}):
            path = hwp_parser.get_kordoc_path()

        self.assertEqual(path, os.path.join(r"D:\tools\kordoc", "dist", "cli.js"))

    def test_default_development_path_uses_repository_engine(self):
        self.assertTrue(hasattr(hwp_parser, "get_kordoc_path"))

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("KORDOC_HOME", None)
            path = Path(hwp_parser.get_kordoc_path())

        self.assertEqual(path.name, "cli.js")
        self.assertEqual(path.parent.parent.name, "kordoc")
        self.assertEqual(path.parent.parent.parent.name, "engine")

    def test_default_node_path_uses_bundled_node(self):
        path = Path(hwp_parser.get_node_path())

        self.assertEqual(path.name, "node.exe")
        self.assertEqual(path.parent.name, "bin")


if __name__ == "__main__":
    unittest.main()
