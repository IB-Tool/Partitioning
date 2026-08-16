# -*- coding: utf-8 -*-
"""Structural tests that don't require QGIS to be available.

Taken over from the former test/test_test.py, which was dissolved. The other
tests that used to live there duplicated coverage found elsewhere or tested
the Python standard library / MagicMock itself and carried no assertion
value, so they were dropped rather than moved.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_plugin_directory_structure():
    """Plugin directory contains the files required for a QGIS plugin."""
    plugin_dir = Path(__file__).parent.parent

    essential_files = [
        'IbToolPartion.py',
        'metadata.txt',
        '__init__.py'
    ]

    for file_name in essential_files:
        file_path = plugin_dir / file_name
        assert file_path.exists(), f"Essential file missing: {file_name}"


def test_plugin_imports_without_qgis():
    """Plugin package imports successfully with all QGIS modules mocked."""
    plugin_dir = Path(__file__).parent.parent
    plugin_parent = str(plugin_dir.parent)
    if plugin_parent not in sys.path:
        sys.path.insert(0, plugin_parent)

    qgis_mocks = {
        'qgis': MagicMock(),
        'qgis.PyQt': MagicMock(),
        'qgis.PyQt.QtCore': MagicMock(),
        'qgis.PyQt.QtGui': MagicMock(),
        'qgis.PyQt.QtWidgets': MagicMock(),
        'qgis.core': MagicMock(),
        'qgis.gui': MagicMock(),
        'qgis.processing': MagicMock(),
        'ibtoolpartion.resources': MagicMock(),
        'ibtoolpartion.IbToolPartion_dialog': MagicMock(),
    }

    with patch.dict('sys.modules', qgis_mocks):
        sys.modules.pop('ibtoolpartion', None)
        sys.modules.pop('ibtoolpartion.IbToolPartion', None)
        try:
            import ibtoolpartion.IbToolPartion  # noqa: F401  # pylint: disable=unused-import
        except Exception as e:  # pylint: disable=broad-exception-caught
            pytest.fail(f"Plugin import failed even with mocked QGIS: {e}")
