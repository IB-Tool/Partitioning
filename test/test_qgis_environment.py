# coding=utf-8
# pylint: skip-file
"""Tests for the plugin's QGIS-related environment and metadata."""

__author__ = 'tim@linfiniti.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from pathlib import Path


class QGISTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def setUp(self):
        self.plugin_dir = Path(__file__).parent.parent

    def test_qgis_environment(self):
        """Plugin directory contains the files required for QGIS provider access."""
        required = [
            'IbToolPartion.py',
            'IbToolPartion_dialog.py',
            '__init__.py',
            'metadata.txt',
        ]
        for name in required:
            self.assertTrue(
                (self.plugin_dir / name).exists(),
                f"Required file missing: {name}"
            )

    def test_projection(self):
        """metadata.txt declares a QGIS minimum version."""
        metadata_path = self.plugin_dir / 'metadata.txt'
        self.assertTrue(metadata_path.exists(), "metadata.txt not found")
        content = metadata_path.read_text(encoding='utf-8')
        self.assertIn(
            'qgisMinimumVersion',
            content,
            "metadata.txt must declare qgisMinimumVersion"
        )


if __name__ == '__main__':
    unittest.main()
