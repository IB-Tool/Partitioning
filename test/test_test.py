# -*- coding: utf-8 -*-
"""
Simple tests that don't require QGIS to be available.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_plugin_directory_structure():
    """Test that plugin has the expected directory structure."""
    plugin_dir = Path(__file__).parent.parent
    
    # Check for essential files
    essential_files = [
        'IbToolPartion.py',
        'metadata.txt',
        '__init__.py'
    ]
    
    for file_name in essential_files:
        file_path = plugin_dir / file_name
        assert file_path.exists(), f"Essential file missing: {file_name}"
    
    print("✓ Plugin directory structure OK")


def test_basic_python_functionality():
    """Test basic Python functionality without QGIS."""
    import tempfile
    import os
    
    # Test temporary file creation
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp_path = tmp.name
    
    assert os.path.exists(tmp_path)
    
    # Clean up
    os.unlink(tmp_path)
    assert not os.path.exists(tmp_path)
    
    print("✓ Basic Python functionality working")


def test_plugin_imports_without_qgis():
    """Test that we can import plugin parts that don't depend on QGIS."""
    plugin_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(plugin_dir))
    
    # Mock QGIS modules before importing
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
        try:
            # Try to import the plugin (this will work with mocked QGIS)
            import IbToolPartion
            print("✓ Plugin import successful with mocked QGIS")
            assert True
        except Exception as e:
            pytest.fail(f"Plugin import failed even with mocked QGIS: {e}")


def test_mock_qgis_interface():
    """Test the mock QGIS interface functionality."""
    from unittest.mock import MagicMock
    
    mock_iface = MagicMock()
    mock_iface.messageBar.return_value.pushMessage = MagicMock()
    mock_iface.addToolBarIcon = MagicMock()
    mock_iface.removeToolBarIcon = MagicMock()
    mock_iface.addPluginToMenu = MagicMock()
    mock_iface.removePluginMenu = MagicMock()
    mock_iface.mainWindow.return_value = MagicMock()
    
    # Test that we can call interface methods
    mock_iface.messageBar().pushMessage("Test", "Message")
    mock_iface.addToolBarIcon(MagicMock())
    
    # Verify calls were made
    assert mock_iface.messageBar.called
    assert mock_iface.addToolBarIcon.called
    
    print("✓ Mock QGIS interface working")


def test_temp_directory_fixture():
    """Test temporary directory creation."""
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    assert temp_path.exists()
    assert temp_path.is_dir()
    
    # Create a test file
    test_file = temp_path / "test.txt"
    test_file.write_text("test content")
    
    assert test_file.exists()
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    assert not temp_path.exists()
    
    print("✓ Temporary directory functionality working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])