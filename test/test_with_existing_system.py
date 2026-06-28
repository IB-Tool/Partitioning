# -*- coding: utf-8 -*-
"""
Tests using the existing QGIS test system.
"""
import os
import tempfile
import pytest
import sys
from pathlib import Path

# Add the test directory to path to import utilities
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

try:
    from utilities import get_qgis_app
    QGIS_SYSTEM_AVAILABLE = True
except ImportError:
    QGIS_SYSTEM_AVAILABLE = False


def test_qgis_app_creation():
    """get_qgis_app() returns a 4-tuple; None values when QGIS is not available."""
    result = get_qgis_app()
    assert isinstance(result, tuple), "get_qgis_app() muss ein Tuple zurückgeben"
    assert len(result) == 4, "get_qgis_app() muss ein 4-Tuple zurückgeben"
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
        pytest.fail("QgsProviderRegistry konnte nicht importiert werden")


def test_basic_python_functionality():
    """Test basic Python functionality without QGIS."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp_path = tmp.name

    assert os.path.exists(tmp_path)

    os.unlink(tmp_path)
    assert not os.path.exists(tmp_path)


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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
