# -*- coding: utf-8 -*-
"""Dialog tests: raw .ui declarations plus a live instance (requires Qt/QGIS)."""
# pylint: disable=possibly-used-before-assignment
# QtWidgets/IbToolPartitionDialog are only bound when _QGIS_AVAILABLE is True
# (see the conditional import block below). TestIbToolPartitionDialogWidgets
# is the only user of them and carries a class-level skipif guard for
# exactly that case, so they are never referenced unbound at runtime -
# pylint's static analysis cannot see that.

__author__ = 'ottmar.hittzfeld@web.de'
__date__ = '2024-12-15'
__copyright__ = 'Copyright 2024, Oliver Harig'

from pathlib import Path

import pytest

from .utilities import get_qgis_app

QGIS_APP, _CANVAS, _IFACE, _PARENT = get_qgis_app()
_QGIS_AVAILABLE = QGIS_APP is not None

if _QGIS_AVAILABLE:
    # Import after get_qgis_app() so the Qt/QGIS bindings are fully
    # initialised before the dialog module (which loads the .ui file via
    # uic.loadUiType at import time) is imported. See
    # test/layer_factories.py header. Guarded behind _QGIS_AVAILABLE so this
    # module still collects (and TestIbToolPartitionDialogUiDefinition still
    # runs) in an environment without QGIS - e.g. a plain venv interpreter.
    from qgis.PyQt import QtWidgets  # noqa: E402  pylint: disable=wrong-import-position
    from ibtoolpartion.IbToolPartion_dialog import (  # noqa: E402  pylint: disable=wrong-import-position
        IbToolPartitionDialog,
    )


class TestIbToolPartitionDialogUiDefinition:
    """Tests against the raw .ui file — no Qt runtime required."""

    @classmethod
    def setup_class(cls):
        """Read the .ui file content once for all tests in this class."""
        ui_path = Path(__file__).parent.parent / 'IbToolPartion_dialog_base.ui'
        cls.ui_content = ui_path.read_text(encoding='utf-8')

    @pytest.mark.unit
    def test_dialog_ok(self):
        """Dialog UI declares a QDialogButtonBox with an Ok button."""
        assert 'QDialogButtonBox::Ok' in self.ui_content

    @pytest.mark.unit
    def test_dialog_cancel(self):
        """Dialog UI declares a QDialogButtonBox with a Cancel button."""
        assert 'QDialogButtonBox::Cancel' in self.ui_content


@pytest.mark.skipif(not _QGIS_AVAILABLE, reason="QGIS is not available in this environment")
class TestIbToolPartitionDialogWidgets:
    """Tests against a live dialog instance."""

    @pytest.fixture
    def dlg(self):
        """Fresh dialog instance for each test."""
        return IbToolPartitionDialog()

    @pytest.mark.integration
    def test_instantiates_without_parent(self):
        """Dialog can be instantiated without a parent widget."""
        dlg = IbToolPartitionDialog(parent=None)
        assert dlg is not None

    @pytest.mark.integration
    def test_has_input_hu_widget(self, dlg):
        """Dialog exposes the Input_HU line edit."""
        assert hasattr(dlg, 'Input_HU')

    @pytest.mark.integration
    def test_has_output_file_widget(self, dlg):
        """Dialog exposes the output_file line edit."""
        assert hasattr(dlg, 'output_file')

    @pytest.mark.integration
    def test_has_cell_size_widget(self, dlg):
        """Dialog exposes the cell_size spin box."""
        assert hasattr(dlg, 'cell_size')

    @pytest.mark.integration
    def test_has_hu_button_widget(self, dlg):
        """Dialog exposes the HU_Button push button."""
        assert hasattr(dlg, 'HU_Button')

    @pytest.mark.integration
    def test_has_output_button_widget(self, dlg):
        """Dialog exposes the Output_Button push button."""
        assert hasattr(dlg, 'Output_Button')

    @pytest.mark.integration
    def test_button_box_accept_sets_result_ok(self, dlg):
        """Emitting button_box.accepted() drives the dialog to Accepted."""
        dlg.button_box.accepted.emit()
        assert dlg.result() == QtWidgets.QDialog.Accepted

    @pytest.mark.integration
    def test_button_box_reject_sets_result_cancel(self, dlg):
        """Emitting button_box.rejected() drives the dialog to Rejected."""
        dlg.button_box.rejected.emit()
        assert dlg.result() == QtWidgets.QDialog.Rejected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
