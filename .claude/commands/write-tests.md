---
description: Use this skill when the user asks to write, create, or add tests for a module, function, or class — for example "schreib Tests für Partitioning", "write tests for a module", "add test coverage for X", "fehlende Tests ergänzen". Invoke automatically whenever a testing task is identified for this QGIS plugin project.
---

# /write-tests — Write Tests for an IbToolPartion Module

Write pytest tests for the module: **$ARGUMENTS**

Follow these steps in order. Do not skip any step.

---

## Step 1 — Read the target module

Search for `$ARGUMENTS` in these locations (in order):
- `$ARGUMENTS.py` (root level)
- Try case variations (e.g. `IbToolPartion` → `ibtoolpartion`)

Read the file completely. Identify:
- All public classes and methods
- Input parameters and their types
- Return values and their types
- Error conditions and how they are handled
- Any calls to `processing.run()` or `safe_processing_run()` — these determine the tier (see Step 3)

## Step 2 — Check for existing tests

Search `test/` for an existing test file for `$ARGUMENTS`:
- `test/test_$ARGUMENTS.py` (snake_case variant)
- Any file matching `test_*$ARGUMENTS*`

If a test file **exists**: extend it, do not replace it.
If no test file exists: create `test/test_<snake_case_name>.py`.

## Step 3 — Consult project rules (mandatory)

Read **all** of these files before writing any code:

1. `ai/core/testing-rules.md` — tier definitions, coverage targets, structure
2. `ai/core/qgis-api-rules.md` — QGIS API compatibility rules
3. `ai/core/constraints.md` — language and naming rules

Also read:
- `test/utilities.py` — QGIS app initialisation helper
- `test/conftest.py` — shared fixtures

## Step 4 — Write the test file

### Tier decision

```
Does the function under test call processing.run()?
├── No  → @pytest.mark.unit
└── Yes → @pytest.mark.integration  (requires Docker / local QGIS)

Is this a boundary or degenerate input?
└── Yes → additionally add @pytest.mark.edge_case
```

### Required structure

```python
import pytest
from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsCoordinateReferenceSystem, QgsPointXY,
)

from .utilities import get_qgis_app

QGIS_APP, _CANVAS, _IFACE, _PARENT = get_qgis_app()

from ibtoolpartion.<ModuleName> import <function_or_class>


class Test$ARGUMENTS:
    """Tests for <module_name>.<function_or_class>."""

    CRS_ID = "EPSG:25833"

    @classmethod
    def setup_class(cls):
        cls.crs = QgsCoordinateReferenceSystem(cls.CRS_ID)

    @pytest.mark.unit
    def test_normal_case(self):
        """<Imperative description of what this test verifies.>"""
        ...
```

### Required geometry assertions (mandatory after every geometry operation)

```python
assert result_layer is not None
assert result_layer.featureCount() > 0
for feat in result_layer.getFeatures():
    geom = feat.geometry()
    assert not geom.isNull(),   "Geometry must not be null"
    assert not geom.isEmpty(),  "Geometry must not be empty"
    assert geom.isGeosValid(),  "Geometry must be GEOS-valid"
```

### Mandatory test cases (minimum)

1. **Normal case** — valid input; check return value, feature count, geometry validity
2. **Empty input layer** — 0 features; verify graceful handling (no crash, defined return)
3. **Null geometry on one feature** — layer with one null-geometry feature; verify no crash
4. At least one **domain-specific edge case** (`@pytest.mark.edge_case`)

### Docstring rule (mandatory)

Every test method must have a one-line docstring in the imperative mood:

```python
def test_partitioning_result_is_valid(self):
    """Returns a valid partitioned layer for standard input."""
```

## Step 5 — Run pylint

Run pylint on the test file:

```bash
pylint test/test_<module_name>.py
```

Fix any warnings introduced by your changes.

## Step 6 — Output

Report:
1. Path of the created/modified test file
2. List of test methods written and what each covers
3. Which tier markers were applied and why
4. Any assumptions made about expected behavior
