# -*- coding: utf-8 -*-
"""
Setup script to add QGIS paths to Python environment for testing.
"""
import sys
import os
from pathlib import Path


def setup_qgis_paths():
    """Add QGIS paths to Python sys.path for testing."""

    # Standard QGIS installation paths for Windows
    qgis_base = r"C:\Program Files\QGIS 3.40.0"

    qgis_paths = [
        os.path.join(qgis_base, "apps", "qgis", "python"),
        os.path.join(qgis_base, "apps", "Python312", "Lib", "site-packages"),
        os.path.join(qgis_base, "apps", "qgis", "python", "plugins"),
    ]

    # Alternative paths (falls QGIS an anderem Ort installiert ist)
    alternative_bases = [
        r"C:\OSGeo4W64",
        r"C:\Program Files\QGIS 3.38.3",
        r"C:\Program Files\QGIS 3.36.3",
    ]

    alternative_paths = []
    for base in alternative_bases:
        if os.path.exists(base):
            alternative_paths.extend([
                os.path.join(base, "apps", "qgis", "python"),
                os.path.join(base, "apps", "Python312", "Lib", "site-packages"),
                os.path.join(base, "apps", "Python39", "Lib", "site-packages"),
                # For older QGIS
            ])

    # Kombiniere alle möglichen Pfade
    all_paths = qgis_paths + alternative_paths

    # Füge existierende Pfade zu sys.path hinzu
    added_paths = []
    for qgis_path in all_paths:
        if os.path.exists(qgis_path) and qgis_path not in sys.path:
            sys.path.insert(0, qgis_path)
            added_paths.append(qgis_path)

    # Setze QGIS-spezifische Umgebungsvariablen
    qgis_prefix_path = os.path.join(qgis_base, "apps", "qgis")
    if os.path.exists(qgis_prefix_path):
        os.environ['QGIS_PREFIX_PATH'] = qgis_prefix_path

    # **WICHTIG**: Setze DLL-Pfade für Windows
    setup_dll_paths(qgis_base)

    return added_paths


def setup_dll_paths(qgis_base):
    """Setup DLL paths for QGIS on Windows."""

    # Wichtige DLL-Pfade für QGIS
    dll_paths = [
        os.path.join(qgis_base, "bin"),
        os.path.join(qgis_base, "apps", "qgis", "bin"),
        os.path.join(qgis_base, "apps", "Python312", "DLLs"),
        os.path.join(qgis_base, "apps", "Qt5", "bin"),
        os.path.join(qgis_base, "apps", "gdal", "bin"),
        os.path.join(qgis_base, "apps", "grass", "grass83", "bin"),
        os.path.join(qgis_base, "apps", "grass", "grass83", "lib"),
    ]

    # PATH Umgebungsvariable erweitern
    current_path = os.environ.get('PATH', '')
    new_paths = []

    for dll_path in dll_paths:
        if os.path.exists(dll_path) and dll_path not in current_path:
            new_paths.append(dll_path)

    if new_paths:
        new_path = ';'.join(new_paths) + ';' + current_path
        os.environ['PATH'] = new_path
        print(f"DLL-Pfade hinzugefügt: {len(new_paths)}")
        for path in new_paths:
            print(f"  - {path}")

    # Weitere wichtige Umgebungsvariablen
    if os.path.exists(os.path.join(qgis_base, "apps", "gdal")):
        os.environ['GDAL_DATA'] = os.path.join(qgis_base, "apps", "gdal",
                                               "share", "gdal")
        os.environ['GDAL_DRIVER_PATH'] = os.path.join(qgis_base, "apps", "gdal",
                                                      "lib", "gdalplugins")

    if os.path.exists(os.path.join(qgis_base, "apps", "proj")):
        os.environ['PROJ_LIB'] = os.path.join(qgis_base, "apps", "proj",
                                              "share", "proj")


def find_qgis_installation():
    """Find QGIS installation path automatically."""
    possible_locations = [
        r"C:\Program Files\QGIS 3.40.0",
        r"C:\Program Files\QGIS 3.38.3",
        r"C:\Program Files\QGIS 3.36.3",
        r"C:\OSGeo4W64",
        r"C:\Program Files (x86)\QGIS 3.40.0",
    ]

    for location in possible_locations:
        if os.path.exists(location):
            print(f"QGIS gefunden in: {location}")
            return location

    print("QGIS-Installation nicht gefunden!")
    return None


def test_qgis_import():
    """Test various QGIS imports step by step."""
    print("\n=== QGIS Import Test ===")

    # Test 1: Basic Qt import
    try:
        from PyQt5.QtCore import QCoreApplication
        print("✓ PyQt5.QtCore erfolgreich importiert")
    except ImportError as e:
        print(f"✗ PyQt5.QtCore Import fehlgeschlagen: {e}")
        return False

    # Test 2: QGIS PyQt import
    try:
        from qgis.PyQt.QtCore import QCoreApplication as QgsQtCore
        print("✓ qgis.PyQt.QtCore erfolgreich importiert")
    except ImportError as e:
        print(f"✗ qgis.PyQt.QtCore Import fehlgeschlagen: {e}")
        return False

    # Test 3: QGIS core import
    try:
        from qgis.core import QgsApplication
        print("✓ qgis.core.QgsApplication erfolgreich importiert")
    except ImportError as e:
        print(f"✗ qgis.core Import fehlgeschlagen: {e}")
        return False

    # Test 4: Full qgis.core import
    try:
        import qgis.core
        print("✓ qgis.core vollständig importiert")
        return True
    except ImportError as e:
        print(f"✗ qgis.core vollständiger Import fehlgeschlagen: {e}")
        return False


if __name__ == "__main__":
    print("=== QGIS-Setup für Tests ===")

    # Finde QGIS Installation
    qgis_location = find_qgis_installation()

    # Füge Pfade hinzu
    added = setup_qgis_paths()

    print(f"\nQGIS Installation: {qgis_location}")
    print(
        f"QGIS_PREFIX_PATH: {os.environ.get('QGIS_PREFIX_PATH', 'Nicht gesetzt')}")
    print(f"Hinzugefügte Python-Pfade: {len(added)}")
    for path in added[:3]:  # Nur erste 3 anzeigen
        print(f"  - {path}")
    if len(added) > 3:
        print(f"  ... und {len(added) - 3} weitere")

    # Teste QGIS Import
    success = test_qgis_import()

    if success:
        print("\n🎉 QGIS-Setup erfolgreich!")
    else:
        print("\n❌ QGIS-Setup fehlgeschlagen")
        print("\nTipp: Versuchen Sie das Setup aus QGIS heraus zu starten:")
        print("  1. Öffnen Sie QGIS")
        print("  2. Öffnen Sie die Python-Konsole")
        print("  3. Führen Sie dieses Script aus")