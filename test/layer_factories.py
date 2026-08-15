"""
Shared layer and geometry factory helpers for IbToolPartition tests.

Import this module AFTER calling get_qgis_app() in your test file so that
qgis.core is fully initialised when the module-level imports run.

Usage in test files:
    from .utilities import get_qgis_app
    QGIS_APP, _CANVAS, _IFACE, _PARENT = get_qgis_app()
    from .layer_factories import (
        make_polygon_layer, make_line_layer, make_point_layer,
        make_square_geom, add_feature_to_layer,
        write_layer_as_shp, write_layer_as_gpkg,
        make_building_grid_layer,
    )
"""

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsVectorFileWriter,
    QgsCoordinateTransformContext,
)


def make_polygon_layer(crs: str = "EPSG:25833", name: str = "test_poly") -> QgsVectorLayer:
    """Return an empty in-memory polygon layer with the given CRS."""
    layer = QgsVectorLayer(f"Polygon?crs={crs}", name, "memory")
    layer.updateFields()
    return layer


def make_line_layer(crs: str = "EPSG:25833", name: str = "test_line") -> QgsVectorLayer:
    """Return an empty in-memory line layer with the given CRS."""
    layer = QgsVectorLayer(f"LineString?crs={crs}", name, "memory")
    layer.updateFields()
    return layer


def make_point_layer(crs: str = "EPSG:25833", name: str = "test_point") -> QgsVectorLayer:
    """Return an empty in-memory point layer with the given CRS."""
    layer = QgsVectorLayer(f"Point?crs={crs}", name, "memory")
    layer.updateFields()
    return layer


def make_square_geom(x0: float, y0: float, size: float) -> QgsGeometry:
    """Return an axis-aligned square QgsGeometry with bottom-left corner at (x0, y0)."""
    return QgsGeometry.fromPolygonXY([[
        QgsPointXY(x0,        y0),
        QgsPointXY(x0 + size, y0),
        QgsPointXY(x0 + size, y0 + size),
        QgsPointXY(x0,        y0 + size),
        QgsPointXY(x0,        y0),
    ]])


def add_feature_to_layer(layer: QgsVectorLayer, geom: QgsGeometry) -> QgsFeature:
    """Add a QgsFeature with the given geometry to layer and return it."""
    feat = QgsFeature(layer.fields())
    feat.setGeometry(geom)
    layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return feat


def _write_layer(layer: QgsVectorLayer, path: str, driver_name: str) -> str:
    """Write layer to path using the given OGR driver and return the path.

    Raises IOError if the write fails, e.g. because of an unwritable path.
    """
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = driver_name
    error = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer, str(path), QgsCoordinateTransformContext(), options
    )
    # writeAsVectorFormatV3 returns a tuple whose first element is a
    # QgsVectorFileWriter.WriterError; NoError == 0.
    if error[0] != QgsVectorFileWriter.NoError:
        raise IOError(f"Failed to write {driver_name} to {path}: {error}")
    return str(path)


def write_layer_as_shp(layer: QgsVectorLayer, path: str) -> str:
    """Write layer to path as an ESRI Shapefile and return the path.

    Needed because processor._load_shp and IbToolPartition.siedgr expect
    file paths, not layer objects, as input.
    """
    return _write_layer(layer, path, "ESRI Shapefile")


def write_layer_as_gpkg(layer: QgsVectorLayer, path: str) -> str:
    """Write layer to path as a GeoPackage and return the path."""
    return _write_layer(layer, path, "GPKG")


def make_building_grid_layer(
    n_x: int,
    n_y: int,
    size: float = 10.0,
    spacing: float = 20.0,
    crs: str = "EPSG:25833",
) -> QgsVectorLayer:
    """Return a polygon layer with an n_x by n_y grid of square buildings.

    Each building is a `size` x `size` square; buildings are spaced
    `spacing` apart (measured between the origins of adjacent cells).
    Used as siedgr() input to build reproducible building-footprint fixtures
    without requiring test data checked into the repository.
    """
    layer = make_polygon_layer(crs, "buildings")
    for i in range(n_x):
        for j in range(n_y):
            x0 = i * spacing
            y0 = j * spacing
            geom = make_square_geom(x0, y0, size)
            add_feature_to_layer(layer, geom)
    return layer
