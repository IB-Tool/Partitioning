# -*- coding: utf-8 -*-
"""Real integration tests for IbToolPartition.siedgr() against QGIS Processing.

Unlike test/test_ibtoolpartion.py (which mocks qgis.processing entirely and
only verifies the call contract), these tests run the twelve processing.run()
steps for real, against building-footprint layers generated in-memory with
test/layer_factories.py and written to tmp_path — no test data checked into
the repository is needed.

Requires a full QGIS Processing environment (Docker). All tests are skipped
automatically when QGIS is unavailable, and again when the
qgis:heatmapkerneldensityestimation algorithm siedgr() depends on is not
registered in the running QGIS/Processing build (checked at collection time,
so the gap is self-documenting no matter which QGIS image runs these tests -
see docs/test-strategy.md, Gap Analysis, on why a silent skip is not enough
in CI).
"""
# pylint: disable=possibly-used-before-assignment
# QgsWkbTypes/QgsVectorLayer/IbToolPartition/the layer_factories imports are
# only bound when _QGIS_AVAILABLE is True (see the conditional import block
# below). Every test that uses them is skipped via pytestmark's skipif
# guards whenever that is not the case, so they are never referenced
# unbound at runtime - pylint's static analysis cannot see that.
from pathlib import Path

import pytest

from .utilities import get_qgis_app

QGIS_APP, _CANVAS, _IFACE, _PARENT = get_qgis_app()

_QGIS_AVAILABLE = QGIS_APP is not None
_ALGORITHM_ID = "qgis:heatmapkerneldensityestimation"
_ALGORITHM_AVAILABLE = False

if _QGIS_AVAILABLE:
    # Import after get_qgis_app() — see test/layer_factories.py header.
    from qgis.core import QgsWkbTypes, QgsVectorLayer  # noqa: E402  pylint: disable=wrong-import-position
    from processing.core.Processing import Processing  # noqa: E402  pylint: disable=wrong-import-position

    Processing.initialize()

    _ALGORITHM_AVAILABLE = (
        QGIS_APP.processingRegistry().algorithmById(_ALGORITHM_ID) is not None
    )

    from ibtoolpartion.IbToolPartion import IbToolPartition  # noqa: E402  pylint: disable=wrong-import-position
    from .layer_factories import (  # noqa: E402  pylint: disable=wrong-import-position
        make_polygon_layer,
        make_square_geom,
        add_feature_to_layer,
        make_building_grid_layer,
        write_layer_as_gpkg,
    )

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _QGIS_AVAILABLE, reason="QGIS is not available in this environment"),
    pytest.mark.skipif(
        _QGIS_AVAILABLE and not _ALGORITHM_AVAILABLE,
        reason=f"{_ALGORITHM_ID} is not registered in this QGIS/Processing build "
               "(documented as a Justified Exclusion in docs/test-strategy.md)",
    ),
]


def _assert_valid_partition_layer(layer):
    """Assert layer is a non-empty, GEOS-valid polygon layer (mandatory checks)."""
    assert layer.isValid(), "Output layer must be a valid OGR layer"
    assert layer.featureCount() > 0, "Result must contain features"
    for feat in layer.getFeatures():
        geom = feat.geometry()
        assert not geom.isNull(), "Geometry must not be null"
        assert not geom.isEmpty(), "Geometry must not be empty"
        assert geom.isGeosValid(), "Geometry must be GEOS-valid"
        assert QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.PolygonGeometry, (
            "Partition geometries must be polygons"
        )


@pytest.fixture
def plugin():
    """IbToolPartition instance bypassing __init__.

    siedgr() only calls self.tr(), which does not touch any instance
    attribute set up in __init__ (locale/QSettings, iface wiring). Bypassing
    __init__ avoids depending on QSettings('locale/userLocale') being
    populated in the test environment, which is unrelated to what siedgr()
    itself does.
    """
    return IbToolPartition.__new__(IbToolPartition)


class TestSiedgrNormalCase:
    """Tests for siedgr() with a single, moderately sized building cluster."""

    def test_output_file_is_created(self, plugin, tmp_path):
        """siedgr() writes the output file to the requested path."""
        buildings = make_building_grid_layer(n_x=3, n_y=3, size=10, spacing=30)
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        plugin.siedgr(input_path, 50, output_path)

        assert Path(output_path).exists(), "siedgr() must write the output file"

    def test_output_layer_has_valid_geometries(self, plugin, tmp_path):
        """siedgr() produces a non-empty layer of GEOS-valid polygons."""
        buildings = make_building_grid_layer(n_x=3, n_y=3, size=10, spacing=30)
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        plugin.siedgr(input_path, 50, output_path)

        result_layer = QgsVectorLayer(output_path, "result", "ogr")
        _assert_valid_partition_layer(result_layer)

    def test_output_has_name_field_with_part_prefix(self, plugin, tmp_path):
        """siedgr() adds a NAME field whose values all carry the PART_ prefix."""
        buildings = make_building_grid_layer(n_x=3, n_y=3, size=10, spacing=30)
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        plugin.siedgr(input_path, 50, output_path)

        result_layer = QgsVectorLayer(output_path, "result", "ogr")
        field_names = [f.name() for f in result_layer.fields()]
        assert "NAME" in field_names, "Output must have a NAME field"
        for feat in result_layer.getFeatures():
            assert str(feat["NAME"]).startswith("PART_"), (
                f"NAME value {feat['NAME']!r} must start with 'PART_'"
            )

    def test_return_value_matches_requested_filename(self, plugin, tmp_path):
        """siedgr() returns exactly the filename argument it was given."""
        buildings = make_building_grid_layer(n_x=3, n_y=3, size=10, spacing=30)
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        result = plugin.siedgr(input_path, 50, output_path)

        assert result == output_path


class TestSiedgrEdgeCases:
    """Boundary and degenerate inputs for siedgr()."""

    @pytest.mark.edge_case
    def test_single_building(self, plugin, tmp_path):
        """siedgr() completes and produces a valid partition for a single building."""
        buildings = make_building_grid_layer(n_x=1, n_y=1, size=10, spacing=30)
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        plugin.siedgr(input_path, 50, output_path)

        result_layer = QgsVectorLayer(output_path, "result", "ogr")
        _assert_valid_partition_layer(result_layer)

    @pytest.mark.edge_case
    @pytest.mark.slow
    def test_very_small_cell_size(self, plugin, tmp_path):
        """siedgr() completes for a small cell_size without an oversized raster.

        Building extent is kept deliberately small alongside cell_size=1 so
        the intermediate heatmap raster stays a handful of pixels wide and
        the test runs in bounded time.
        """
        buildings = make_building_grid_layer(n_x=2, n_y=2, size=5, spacing=10)
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        plugin.siedgr(input_path, 1, output_path)

        result_layer = QgsVectorLayer(output_path, "result", "ogr")
        _assert_valid_partition_layer(result_layer)

    @pytest.mark.edge_case
    def test_two_distant_clusters_yield_multiple_partitions(self, plugin, tmp_path):
        """siedgr() splits two widely separated building clusters into >= 2 partitions."""
        cell_size = 50
        buildings = make_polygon_layer(name="buildings")
        # Cluster A around the origin.
        for i in range(3):
            for j in range(3):
                add_feature_to_layer(buildings, make_square_geom(i * 30, j * 30, 10))
        # Cluster B far enough away (5 km) that the two heatmap peaks and
        # their Voronoi regions cannot merge into one partition.
        offset = 5000
        for i in range(3):
            for j in range(3):
                add_feature_to_layer(
                    buildings, make_square_geom(offset + i * 30, offset + j * 30, 10)
                )
        input_path = write_layer_as_gpkg(buildings, str(tmp_path / "buildings.gpkg"))
        output_path = str(tmp_path / "output.gpkg")

        plugin.siedgr(input_path, cell_size, output_path)

        result_layer = QgsVectorLayer(output_path, "result", "ogr")
        _assert_valid_partition_layer(result_layer)
        assert result_layer.featureCount() >= 2, (
            "Two widely separated building clusters must yield at least two partitions"
        )
