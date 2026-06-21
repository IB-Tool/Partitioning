# -*- coding: utf-8 -*-
"""Simple tests that don't require QGIS to be available."""
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_plugin_directory_structure():
    """Test that plugin has the expected directory structure."""
    plugin_dir = Path(__file__).parent.parent

    essential_files = [
        'IbToolPartion.py',
        'metadata.txt',
        '__init__.py'
    ]

    for file_name in essential_files:
        file_path = plugin_dir / file_name
        assert file_path.exists(), f"Essential file missing: {file_name}"


def test_basic_python_functionality():
    """Test basic Python functionality without QGIS."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp_path = tmp.name

    assert os.path.exists(tmp_path)

    os.unlink(tmp_path)
    assert not os.path.exists(tmp_path)


def test_plugin_imports_without_qgis():
    """Test that we can import plugin parts that don't depend on QGIS."""
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


def test_mock_qgis_interface():
    """Test the mock QGIS interface functionality."""
    mock_iface = MagicMock()
    mock_iface.messageBar.return_value.pushMessage = MagicMock()
    mock_iface.addToolBarIcon = MagicMock()
    mock_iface.removeToolBarIcon = MagicMock()
    mock_iface.addPluginToMenu = MagicMock()
    mock_iface.removePluginMenu = MagicMock()
    mock_iface.mainWindow.return_value = MagicMock()

    mock_iface.messageBar().pushMessage("Test", "Message")
    mock_iface.addToolBarIcon(MagicMock())

    assert mock_iface.messageBar.called
    assert mock_iface.addToolBarIcon.called


def test_temp_directory_fixture():
    """Test temporary directory creation."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    assert temp_path.exists()
    assert temp_path.is_dir()

    test_file = temp_path / "test.txt"
    test_file.write_text("test content", encoding="utf-8")

    assert test_file.exists()

    shutil.rmtree(temp_dir, ignore_errors=True)
    assert not temp_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
