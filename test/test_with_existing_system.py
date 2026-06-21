# -*- coding: utf-8 -*-
"""
Tests using the existing QGIS test system.
"""
import pytest
import sys
import os
from pathlib import Path

# Add the test directory to path to import utilities
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

try:
    from utilities import get_qgis_app
    QGIS_SYSTEM_AVAILABLE = True
except ImportError:
    QGIS_SYSTEM_AVAILABLE = False


@pytest.mark.skipif(not QGIS_SYSTEM_AVAILABLE, reason="QGIS test system nicht verfügbar")
def test_qgis_app_creation():
    """Test that we can create a QGIS app using the existing system."""
    qgis_app, canvas, iface, parent = get_qgis_app()
    
    # Check if QGIS was successfully initialized
    if qgis_app is None:
        pytest.skip("QGIS konnte nicht initialisiert werden")
    
    assert qgis_app is not None
    assert canvas is not None
    assert iface is not None
    assert parent is not None
    
    print("✓ QGIS App erfolgreich erstellt")


@pytest.mark.skipif(not QGIS_SYSTEM_AVAILABLE, reason="QGIS test system nicht verfügbar")
def test_qgis_providers():
    """Test that QGIS providers are available."""
    qgis_app, canvas, iface, parent = get_qgis_app()
    
    if qgis_app is None:
        pytest.skip("QGIS konnte nicht initialisiert werden")
    
    try:
        from qgis.core import QgsProviderRegistry
        r = QgsProviderRegistry.instance()
        providers = r.providerList()
        
        assert 'gdal' in providers
        assert 'ogr' in providers
        print(f"✓ Verfügbare Provider: {providers}")
        
    except ImportError:
        pytest.fail("QgsProviderRegistry konnte nicht importiert werden")


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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])