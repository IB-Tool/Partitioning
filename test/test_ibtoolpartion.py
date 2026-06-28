# -*- coding: utf-8 -*-
"""Tests for IbToolPartion.IbToolPartition plugin class."""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PLUGIN_PARENT = str(Path(__file__).parent.parent.parent)
if _PLUGIN_PARENT not in sys.path:
    sys.path.insert(0, _PLUGIN_PARENT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_qgis_mocks():
    """Return a sys.modules patch dict with all QGIS dependencies mocked."""
    mock_qtcore = MagicMock()
    mock_qsettings = MagicMock()
    mock_qsettings.value.return_value = "de_DE"
    mock_qtcore.QSettings.return_value = mock_qsettings
    mock_qtcore.QCoreApplication.translate.side_effect = lambda ctx, msg: msg

    return {
        "qgis": MagicMock(),
        "qgis.PyQt": MagicMock(),
        "qgis.PyQt.QtCore": mock_qtcore,
        "qgis.PyQt.QtGui": MagicMock(),
        "qgis.PyQt.QtWidgets": MagicMock(),
        "qgis.core": MagicMock(),
        "qgis.gui": MagicMock(),
        "ibtoolpartion.resources": MagicMock(),
        "ibtoolpartion.IbToolPartion_dialog": MagicMock(),
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def plugin_class():
    """Import IbToolPartition once per module with all QGIS modules mocked."""
    mocks = _build_qgis_mocks()
    with patch.dict("sys.modules", mocks):
        sys.modules.pop("ibtoolpartion.IbToolPartion", None)
        from ibtoolpartion.IbToolPartion import IbToolPartition  # noqa: PLC0415
        yield IbToolPartition


@pytest.fixture
def mock_iface():
    """Fresh mock QGIS interface for each test."""
    iface = MagicMock()
    iface.mainWindow.return_value = MagicMock()
    iface.messageBar.return_value = MagicMock()
    return iface


@pytest.fixture
def plugin(plugin_class, mock_iface):
    """Fresh IbToolPartition instance for each test."""
    return plugin_class(mock_iface)


# ---------------------------------------------------------------------------
# Tests — constructor
# ---------------------------------------------------------------------------

class TestIbToolPartitionInit:
    """Tests for IbToolPartition.__init__."""

    @pytest.mark.unit
    def test_plugin_dir_points_to_module_directory(self, plugin):
        """Sets plugin_dir to the directory that contains IbToolPartion.py."""
        expected = str(Path(__file__).parent.parent)
        assert plugin.plugin_dir == expected

    @pytest.mark.unit
    def test_iface_is_stored_as_attribute(self, plugin, mock_iface):
        """Stores the iface argument as self.iface."""
        assert plugin.iface is mock_iface

    @pytest.mark.unit
    def test_first_start_is_none_before_initgui(self, plugin):
        """first_start is None before initGui() has been called."""
        assert plugin.first_start is None

    @pytest.mark.unit
    def test_actions_list_is_empty_on_creation(self, plugin):
        """actions list is empty directly after construction."""
        assert plugin.actions == []


# ---------------------------------------------------------------------------
# Tests — tr()
# ---------------------------------------------------------------------------

class TestIbToolPartitionTr:
    """Tests for IbToolPartition.tr."""

    @pytest.mark.unit
    def test_tr_returns_the_input_message(self, plugin):
        """tr() returns the (mock-translated) message string unchanged."""
        assert plugin.tr("Hello") == "Hello"


# ---------------------------------------------------------------------------
# Tests — add_action()
# ---------------------------------------------------------------------------

class TestIbToolPartitionAddAction:
    """Tests for IbToolPartition.add_action."""

    @pytest.mark.unit
    def test_returns_a_non_none_action(self, plugin):
        """add_action() returns the created action object."""
        action = plugin.add_action(":/icon.png", "Test", lambda: None, parent=MagicMock())
        assert action is not None

    @pytest.mark.unit
    def test_appends_action_to_self_actions(self, plugin):
        """add_action() appends the new action to self.actions."""
        before = len(plugin.actions)
        plugin.add_action(":/icon.png", "Test", lambda: None, parent=MagicMock())
        assert len(plugin.actions) == before + 1

    @pytest.mark.unit
    def test_calls_addtoolbaricon_when_enabled(self, plugin, mock_iface):
        """add_action() calls iface.addToolBarIcon when add_to_toolbar=True."""
        plugin.add_action(":/icon.png", "Test", lambda: None, add_to_toolbar=True, parent=MagicMock())
        mock_iface.addToolBarIcon.assert_called()

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_skips_addtoolbaricon_when_disabled(self, plugin, mock_iface):
        """add_action() does not call iface.addToolBarIcon when add_to_toolbar=False."""
        plugin.add_action(":/icon.png", "Test", lambda: None, add_to_toolbar=False, parent=MagicMock())
        mock_iface.addToolBarIcon.assert_not_called()

    @pytest.mark.unit
    def test_calls_addplugintomenu_when_enabled(self, plugin, mock_iface):
        """add_action() calls iface.addPluginToMenu when add_to_menu=True."""
        plugin.add_action(":/icon.png", "Test", lambda: None, add_to_menu=True, parent=MagicMock())
        mock_iface.addPluginToMenu.assert_called()

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_skips_addplugintomenu_when_disabled(self, plugin, mock_iface):
        """add_action() does not call iface.addPluginToMenu when add_to_menu=False."""
        plugin.add_action(":/icon.png", "Test", lambda: None, add_to_menu=False, parent=MagicMock())
        mock_iface.addPluginToMenu.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — initGui()
# ---------------------------------------------------------------------------

class TestIbToolPartitionInitGui:
    """Tests for IbToolPartition.initGui."""

    @pytest.mark.unit
    def test_sets_first_start_to_true(self, plugin):
        """initGui() sets first_start to True."""
        plugin.initGui()
        assert plugin.first_start is True

    @pytest.mark.unit
    def test_registers_exactly_one_action(self, plugin):
        """initGui() adds exactly one entry to self.actions."""
        count_before = len(plugin.actions)
        plugin.initGui()
        assert len(plugin.actions) == count_before + 1


# ---------------------------------------------------------------------------
# Tests — unload()
# ---------------------------------------------------------------------------

class TestIbToolPartitionUnload:
    """Tests for IbToolPartition.unload."""

    @pytest.mark.unit
    def test_calls_removetoolbaricon_for_every_action(self, plugin, mock_iface):
        """unload() calls iface.removeToolBarIcon for every registered action."""
        plugin.initGui()
        mock_iface.removeToolBarIcon.reset_mock()
        plugin.unload()
        assert mock_iface.removeToolBarIcon.call_count >= 1

    @pytest.mark.unit
    def test_calls_removepluginmenu_for_every_action(self, plugin, mock_iface):
        """unload() calls iface.removePluginMenu for every registered action."""
        plugin.initGui()
        mock_iface.removePluginMenu.reset_mock()
        plugin.unload()
        assert mock_iface.removePluginMenu.call_count >= 1


# ---------------------------------------------------------------------------
# Tests — select_output_file()
# ---------------------------------------------------------------------------

class TestIbToolPartitionSelectOutputFile:
    """Tests for IbToolPartition.select_output_file."""

    @pytest.mark.unit
    def test_returns_silently_when_dlg_attribute_is_absent(self, plugin):
        """select_output_file() exits without error when dlg has not been created."""
        if hasattr(plugin, "dlg"):
            del plugin.dlg
        plugin.select_output_file()  # must not raise

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_returns_silently_when_dlg_is_none(self, plugin):
        """select_output_file() exits without error when dlg is explicitly None."""
        plugin.dlg = None
        plugin.select_output_file()  # must not raise


# ---------------------------------------------------------------------------
# Tests — run() validation
# ---------------------------------------------------------------------------

class TestIbToolPartitionRunValidation:
    """Tests for input validation inside IbToolPartition.run()."""

    def _prepare_dialog(self, plugin, input_path="", cell_size="10", output_path="out.shp"):
        """Configure a mock dialog so run() skips dialog creation and accepts input."""
        plugin.first_start = False
        mock_dlg = MagicMock()
        mock_dlg.exec_.return_value = 1
        mock_dlg.Input_HU.text.return_value = input_path
        mock_dlg.cell_size.text.return_value = cell_size
        mock_dlg.output_file.text.return_value = output_path
        plugin.dlg = mock_dlg

    @pytest.mark.unit
    def test_empty_input_path_triggers_error_message(self, plugin, mock_iface):
        """run() pushes an error message when the input file path is empty."""
        self._prepare_dialog(plugin, input_path="")
        plugin.run()
        mock_iface.messageBar.return_value.pushMessage.assert_called()

    @pytest.mark.unit
    def test_nonexistent_input_file_triggers_error_message(self, plugin, mock_iface):
        """run() pushes an error message when the input file does not exist on disk."""
        self._prepare_dialog(plugin, input_path="/does/not/exist.shp")
        plugin.run()
        mock_iface.messageBar.return_value.pushMessage.assert_called()

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_nonnumeric_cell_size_triggers_error_message(self, plugin, mock_iface):
        """run() pushes an error message when cell_size cannot be converted to int."""
        with tempfile.NamedTemporaryFile(suffix=".shp", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self._prepare_dialog(plugin, input_path=tmp_path, cell_size="abc")
            mock_iface.messageBar.return_value.pushMessage.reset_mock()
            plugin.run()
            mock_iface.messageBar.return_value.pushMessage.assert_called()
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    def test_empty_output_path_triggers_error_message(self, plugin, mock_iface):
        """run() pushes an error message when the output file path is empty."""
        with tempfile.NamedTemporaryFile(suffix=".shp", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self._prepare_dialog(plugin, input_path=tmp_path, cell_size="10", output_path="")
            mock_iface.messageBar.return_value.pushMessage.reset_mock()
            plugin.run()
            mock_iface.messageBar.return_value.pushMessage.assert_called()
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Tests — siedgr() (unit — all processing calls mocked)
# ---------------------------------------------------------------------------

class TestIbToolPartitionSiedgr:
    """Tests for IbToolPartition.siedgr."""

    @pytest.mark.unit
    def test_siedgr_returns_the_filename_argument(self, plugin):
        """siedgr() returns the filename parameter as its output path."""
        result = plugin.siedgr("input.shp", 100, "output.shp")
        assert result == "output.shp"

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_siedgr_accepts_minimum_cell_size_of_one(self, plugin):
        """siedgr() completes without error when cell_size=1."""
        result = plugin.siedgr("input.shp", 1, "output.shp")
        assert result == "output.shp"

    @pytest.mark.integration
    def test_siedgr_output_has_features(self, plugin):
        """siedgr() runs all 12 processing steps and threads the output path to the final step."""
        processing = sys.modules["qgis"].processing
        processing.run.reset_mock()

        plugin.siedgr("input.shp", 100, "output.shp")

        assert processing.run.call_count == 12, (
            f"Expected 12 processing.run calls, got {processing.run.call_count}"
        )
        # The last call must use the requested output path.
        last_call = processing.run.call_args_list[-1]
        assert last_call.args[1]['OUTPUT'] == "output.shp"

    @pytest.mark.integration
    def test_siedgr_output_contains_name_field(self, plugin):
        """siedgr() passes FIELD_NAME='NAME' and FORMULA=\"'PART_' || $id\" to fieldcalculator."""
        processing = sys.modules["qgis"].processing
        processing.run.reset_mock()

        plugin.siedgr("input.shp", 100, "output.shp")

        fieldcalc_calls = [
            c for c in processing.run.call_args_list
            if c.args[0] == "native:fieldcalculator"
        ]
        assert len(fieldcalc_calls) == 1, "Exactly one fieldcalculator call expected"
        params = fieldcalc_calls[0].args[1]
        assert params['FIELD_NAME'] == 'NAME'
        assert "'PART_' || $id" in params['FORMULA']
        assert params['OUTPUT'] == "output.shp"
