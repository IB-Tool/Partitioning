# coding=utf-8
# pylint: skip-file
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ottmar.hittzfeld@web.de'
__date__ = '2024-12-15'
__copyright__ = 'Copyright 2024, Oliver Harig'

import unittest
import pytest
pytest.importorskip("qgis.PyQt", reason="QGIS not available")
from qgis.PyQt.QtGui import QIcon  # noqa: E402


class IbToolPartitionResourcesTest(unittest.TestCase):
    """Test resources work."""

    def setUp(self):
        """Runs before each test."""

    def tearDown(self):
        """Runs after each test."""

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/IbToolPartition/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())


if __name__ == "__main__":
    suite = unittest.makeSuite(IbToolPartitionResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
