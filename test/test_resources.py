# coding=utf-8
# pylint: skip-file
"""Resources test."""

__author__ = 'ottmar.hittzfeld@web.de'
__date__ = '2024-12-15'
__copyright__ = 'Copyright 2024, Oliver Harig'

import unittest
from pathlib import Path


class IbToolPartitionResourcesTest(unittest.TestCase):
    """Test resources work."""

    def setUp(self):
        """Runs before each test."""
        self.plugin_dir = Path(__file__).parent.parent

    def tearDown(self):
        """Runs after each test."""

    def test_icon_png(self):
        """icon.png exists in the plugin directory."""
        icon_path = self.plugin_dir / 'icon.png'
        self.assertTrue(icon_path.exists(), f"icon.png not found at {icon_path}")


if __name__ == "__main__":
    suite = unittest.makeSuite(IbToolPartitionResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
