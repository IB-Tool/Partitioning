# coding=utf-8
# pylint: skip-file
"""Dialog test — checks the UI file without requiring a Qt runtime."""

__author__ = 'ottmar.hittzfeld@web.de'
__date__ = '2024-12-15'
__copyright__ = 'Copyright 2024, Oliver Harig'

import unittest
from pathlib import Path


class IbToolPartitionDialogTest(unittest.TestCase):
    """Test dialog UI definition."""

    def setUp(self):
        """Runs before each test."""
        ui_path = Path(__file__).parent.parent / 'IbToolPartion_dialog_base.ui'
        self.ui_content = ui_path.read_text(encoding='utf-8')

    def tearDown(self):
        """Runs after each test."""

    def test_dialog_ok(self):
        """Dialog UI declares a QDialogButtonBox with an Ok button."""
        self.assertIn('QDialogButtonBox::Ok', self.ui_content)

    def test_dialog_cancel(self):
        """Dialog UI declares a QDialogButtonBox with a Cancel button."""
        self.assertIn('QDialogButtonBox::Cancel', self.ui_content)


if __name__ == "__main__":
    suite = unittest.makeSuite(IbToolPartitionDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
