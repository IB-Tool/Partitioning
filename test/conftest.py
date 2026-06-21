# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for IbToolPartition plugin tests.
"""
import pytest
import tempfile
import shutil
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock


@pytest.fixture
def temp_dir():
    """
    Fixture that provides a temporary directory for test files.
    """
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_shapefile_path():
    """
    Fixture that provides path to test shapefile.
    """
    test_data_dir = Path(__file__).parent.parent / "Test_data"
    return test_data_dir


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


@pytest.fixture
def mock_qgis_modules():
    """
    Fixture that provides mocked QGIS modules.
    """
    from unittest.mock import patch, MagicMock
    
    qgis_mocks = {
        'qgis': MagicMock(),
        'qgis.PyQt': MagicMock(),
        'qgis.PyQt.QtCore': MagicMock(),
        'qgis.PyQt.QtGui': MagicMock(), 
        'qgis.PyQt.QtWidgets': MagicMock(),
        'qgis.core': MagicMock(),
        'qgis.gui': MagicMock(),
        'qgis.processing': MagicMock(),
    }
    
    with patch.dict('sys.modules', qgis_mocks):
        yield qgis_mocks