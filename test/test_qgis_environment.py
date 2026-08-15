# coding=utf-8
# pylint: skip-file
"""Tests for the plugin's QGIS-related environment and metadata."""

__author__ = 'tim@linfiniti.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
from pathlib import Path

import pytest

from .utilities import get_qgis_app


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


def test_qgis_app_creation():
    """get_qgis_app() returns a 4-tuple; None values when QGIS is not available."""
    result = get_qgis_app()
    assert isinstance(result, tuple), "get_qgis_app() must return a tuple"
    assert len(result) == 4, "get_qgis_app() must return a 4-tuple"
    qgis_app, canvas, iface, parent = result
    if qgis_app is not None:
        assert canvas is not None
        assert iface is not None
        assert parent is not None


def test_qgis_providers():
    """QGIS providers are accessible when QGIS is available; None-tuple otherwise."""
    qgis_app, canvas, iface, parent = get_qgis_app()
    if qgis_app is None:
        assert (canvas, iface, parent) == (None, None, None)
        return
    try:
        from qgis.core import QgsProviderRegistry
        r = QgsProviderRegistry.instance()
        providers = r.providerList()
        assert 'gdal' in providers
        assert 'ogr' in providers
    except ImportError:
        pytest.fail("QgsProviderRegistry could not be imported")


if __name__ == '__main__':
    unittest.main()
