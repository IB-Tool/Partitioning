# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for IbToolPartition plugin tests.

CRITICAL: no QGIS imports in this file. conftest.py is loaded as a pytest
plugin before test collection; importing qgis.core here triggers QGIS' own
import hook (qgis.utils._import) and causes a circular-import error. QGIS
imports belong in the test modules themselves, after get_qgis_app().
"""
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# The plugin folder name ('ibtoolpartion') is already a valid Python
# identifier, so - unlike IB-Tool-3 - no types.ModuleType alias stub is
# needed here. Adding the parent directory to sys.path makes
# 'import ibtoolpartion.X' resolve locally exactly as it does in the
# container, where PYTHONPATH=/plugins and the plugin lives at
# /plugins/ibtoolpartion.
_PLUGIN_PARENT = str(Path(__file__).resolve().parent.parent.parent)
if _PLUGIN_PARENT not in sys.path:
    sys.path.insert(0, _PLUGIN_PARENT)


@pytest.fixture
def temp_dir():
    """
    Fixture that provides a temporary directory for test files.
    """
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_qgis_interface():
    """
    Fixture that provides a mock QGIS interface.
    """
    mock_iface = MagicMock()
    mock_iface.messageBar.return_value.pushMessage = MagicMock()
    mock_iface.addToolBarIcon = MagicMock()
    mock_iface.removeToolBarIcon = MagicMock()
    mock_iface.addPluginToMenu = MagicMock()
    mock_iface.removePluginMenu = MagicMock()
    mock_iface.mainWindow.return_value = MagicMock()
    return mock_iface


@pytest.fixture
def plugin_dir():
    """
    Fixture that provides the plugin directory path.
    """
    return Path(__file__).parent.parent
