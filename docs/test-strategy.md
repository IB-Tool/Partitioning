# Test Strategy

This document is the single authoritative reference for **why** the test suite is structured the way it is, **how** to choose the right test tier for a new test, and **where** known coverage gaps exist. Consult it before writing any new test or assessing CI failures.

**What this document is not:**
- A tutorial on pytest syntax — see the pytest documentation.
- A list of tactical rules for geometry checks or test structure — see [`ai/core/testing-rules.md`](../ai/core/testing-rules.md).

This plugin is a companion to **[IB-Tool 3](https://github.com/IB-Tool/IB-Tool-3)** and mirrors its testing conventions at a scale appropriate for a single-module plugin. See [IB-Tool 3's own `docs/test-strategy.md`](https://github.com/IB-Tool/IB-Tool-3/blob/master/docs/test-strategy.md) for the full-size version of this document.

---

## Test Philosophy

### Geometry bugs produce plausible-looking wrong results

`siedgr()` chains twelve `processing.run()` calls (centroids → heatmap → pixels-to-points → Voronoi → dissolve → line explode → distance-based cleanup → merge → polygonize → field calculator). A single step that silently returns an empty or invalid geometry does not raise — it just produces a wrong partition that still opens in QGIS. This is why **geometry validity checks (`isNull`, `isEmpty`, `isGeosValid`) are mandatory** for every test that touches `siedgr()`'s output, not just a feature-count check.

### `processing.run()` is the unit/integration boundary

The demarcation between unit and integration tests is not "uses QGIS API" but specifically **whether `processing.run()` is called**. `IbToolPartition.__init__`, `tr()`, `add_action()`, `initGui()`, `unload()`, and the input-validation branches of `run()` touch no Processing algorithm and are unit-testable against a fully mocked `qgis` package. `siedgr()` calls `processing.run()` twelve times and is the integration boundary.

### The mocked call-contract test and the real integration test answer different questions

`test_ibtoolpartion.py::TestIbToolPartitionSiedgr` mocks `qgis.processing` entirely and asserts *what* `siedgr()` asks Processing to do (call count, algorithm IDs, parameter dicts) — cheap, fast, catches accidental parameter regressions. `test_siedgr_integration.py` runs the real pipeline against a live QGIS Processing environment and asserts *what actually comes out* (valid polygons, `NAME` field, correct partition count). Both are needed; neither substitutes for the other. Do not mark the mocked contract test `integration` — it is a unit test of a call contract, not of QGIS behaviour.

### Error paths are first-class citizens

Empty input paths, non-existent files, non-numeric cell sizes, and empty output paths are guaranteed user inputs, not edge cases to defer. Every validation branch in `IbToolPartition.run()` is tested explicitly via `mock_iface.messageBar().pushMessage` assertions.

### Tests document expected behavior

`radius = 2 * cell_size`, the `'PART_' || $id` naming formula, and the `qgis:heatmapkerneldensityestimation` dependency are not obvious from reading `siedgr()`'s twelve processing calls in isolation. Test docstrings and assertion messages make these expectations explicit rather than requiring a re-read of the source.

---

## Test Taxonomy

Four tiers are used. Every test must carry exactly one tier marker and may additionally carry `edge_case`.

### Unit (`@pytest.mark.unit`)

**Definition:** No call to `processing.run()` against a real QGIS Processing registry. May mock `qgis.processing` entirely to assert call contracts.

**When to use:** Constructor/lifecycle tests, `run()` input validation, the `siedgr()` call-contract tests, dialog `.ui`-file checks.

**Execution:** Runs anywhere Python + QGIS libraries are installed (mocked-QGIS tests run without QGIS at all). Does not require Docker.

**Example targets:** `IbToolPartion.py` (everything except the real `siedgr()` pipeline), `IbToolPartion_dialog.py` `.ui` declarations.

### Integration (`@pytest.mark.integration`)

**Definition:** Calls `processing.run()` for real, or instantiates a live Qt/QGIS widget via `get_qgis_app()`.

**When to use:** Testing the real `siedgr()` pipeline end to end, or testing that the dialog widgets exist and respond on a live `QDialog` instance.

**Execution:** Requires Docker (`docker run --rm qgis-plugin-test`) or a local QGIS installation with Processing initialized. Automatically skipped when QGIS is unavailable or when `qgis:heatmapkerneldensityestimation` is not registered in the running Processing build (checked at collection time in `test_siedgr_integration.py`).

**Example targets:** `test_siedgr_integration.py`, the live-widget tests in `test_IbToolPartion_dialog.py`, `test_qgis_environment.py`.

### Edge case (`@pytest.mark.edge_case`)

**Definition:** Cross-cutting tag combined with `unit` or `integration`. Marks a test that exercises a boundary or degenerate input.

**Catalog of mandatory edge cases for this plugin:**
- `add_to_toolbar=False` / `add_to_menu=False` on `add_action()`
- `dlg` attribute absent or `None` on `select_output_file()`
- Non-numeric `cell_size` in `run()`
- `cell_size=1` (minimum plausible value) passed to `siedgr()`
- A single building as `siedgr()` input
- Two widely separated building clusters (must yield ≥ 2 partitions)

### Performance (`@pytest.mark.performance` + `@pytest.mark.slow`)

**Definition:** Exercises time or memory bounds, or a parameter combination known to be runtime-sensitive (e.g. a very small `cell_size`, which inflates the intermediate heatmap raster). Always carries both `performance`-adjacent care and `slow` so it can be excluded from fast local runs via `-m "not slow"`.

**Current use:** `test_siedgr_integration.py::TestSiedgrEdgeCases::test_very_small_cell_size` is marked `slow` (and `edge_case`) because a small `cell_size` increases raster resolution; the building extent is kept deliberately tiny to bound runtime. No dedicated `@pytest.mark.performance`-only test exists yet — see Gap Analysis.

---

## Coverage Targets

Per-category floor values, not aspirational goals. Coverage below these thresholds signals a gap to close before merging new features.

| Module | Target |
|---|---|
| `IbToolPartion.py` (excluding `siedgr()`) | 80% |
| `IbToolPartion.py` `siedgr()` | 75% |
| `IbToolPartion_dialog.py` | 65% |
| `scripts/` | 90% |
| **Overall project** | **70%** |

---

## Test Data and Fixture Strategy

### Shared vs. per-file factories

**`conftest.py`** handles only pytest infrastructure: it adds the plugin's parent directory to `sys.path` so `import ibtoolpartion.X` resolves both locally and in the container (`PYTHONPATH=/plugins`), plus generic fixtures (`temp_dir`, `plugin_dir`, `mock_qgis_interface`). It does **not** import QGIS modules — doing so would trigger a circular import error via `qgis.utils._import` before QGIS is initialized.

**`test/layer_factories.py`** is the canonical home for shared layer and geometry factory helpers. It is a regular Python module (not a pytest plugin) and must be imported **after** calling `get_qgis_app()` in each test file:

```python
from .utilities import get_qgis_app
QGIS_APP, _CANVAS, _IFACE, _PARENT = get_qgis_app()
from .layer_factories import (
    make_polygon_layer, make_line_layer, make_point_layer,
    make_square_geom, add_feature_to_layer,
    write_layer_as_shp, write_layer_as_gpkg,
    make_building_grid_layer,
)
```

Current functions in `layer_factories.py`:
- `make_polygon_layer(crs, name)` / `make_line_layer(crs, name)` / `make_point_layer(crs, name)` — empty in-memory layers
- `make_square_geom(x0, y0, size)` — axis-aligned square `QgsGeometry`
- `add_feature_to_layer(layer, geom)` — adds a `QgsFeature` and returns it
- `write_layer_as_shp(layer, path)` / `write_layer_as_gpkg(layer, path)` — needed because `IbToolPartition.siedgr()` takes file paths, not layer objects
- `make_building_grid_layer(n_x, n_y, size, spacing, crs)` — building-footprint grid used as `siedgr()` input

### Fixture scope rules

| Fixture type | Scope |
|---|---|
| `QgsVectorLayer` instances | `function` — layers are mutable; reuse across tests causes interference |
| `QgsApplication` (QGIS singleton, via `get_qgis_app()`) | module-level singleton, cached across the whole test run — expensive to initialize, safe to share read-only |
| File paths (`tmp_path`) | `function` (pytest built-in) |

---

## Module-to-Test Mapping

| Production module | Test file | ~Tests | Dominant tier | Notable gaps |
|---|---|---|---|---|
| `IbToolPartion.py` (`__init__`, `tr`, `add_action`, `initGui`, `unload`, `select_output_file`, `run()` validation) | `test_ibtoolpartion.py` | 21 | unit | Full `run()` success path (dialog `exec_()` accepted → `siedgr()` called → success message) is not covered; only the four validation-error branches are |
| `IbToolPartion.py` `siedgr()` — call contract | `test_ibtoolpartion.py::TestIbToolPartitionSiedgr` | 4 | unit | — |
| `IbToolPartion.py` `siedgr()` — real pipeline | `test_siedgr_integration.py` | 7 | integration | No `@pytest.mark.performance` test with a large (50+) building set |
| `IbToolPartion_dialog.py` | `test_IbToolPartion_dialog.py` | 10 | unit (`.ui` text) + integration (live widgets) | `select_input_file`/`select_output_file` → `QFileDialog` interaction and the `HU_Button`/`Output_Button` signal wiring in `run()` are not exercised |
| `__init__.py` `classFactory()` | `test_init.py` | 1 | smoke | `classFactory()` itself is untested — needs a live `iface` from the running QGIS application (see Justified Exclusions) |
| `resources.py` | `test_resources.py` | 1 | smoke | Generated file; icon presence only |
| `i18n/*.qm` | `test_translations.py` | 1 | smoke | — |
| Plugin folder / import structure | `test_plugin_structure.py` | 2 | smoke | — |
| QGIS environment / Processing availability | `test_qgis_environment.py` | 4 | smoke / integration | — |
| `scripts/create_release_zip.py` | `test_create_release_zip.py` | 40 | unit | Pure-Python; no QGIS dependency |
| `Partitioning.pyt` | — | 0 | — | Justified Exclusion — ArcGIS toolbox, not part of the QGIS plugin runtime |

---

## Decision Guide for New Tests

Use this checklist when adding a new test.

### Step 1 — Identify what changed

- New function or class → write a test for its normal behavior + at least one edge case.
- Bug fix → write a regression test that reproduces the original bug, then verifies the fix.
- Edge case discovered during review → add to the existing test class under `@pytest.mark.edge_case`.

### Step 2 — Choose the tier

```text
Does the function under test call processing.run() against a real registry?
├── No  → @pytest.mark.unit
└── Yes → @pytest.mark.integration
            (also requires Docker / local QGIS for execution)

Is this testing a boundary / degenerate input?
└── Yes → additionally add @pytest.mark.edge_case

Does it measure runtime/scaling, or use a parameter combination known
to be runtime-sensitive (e.g. tiny cell_size)?
└── Yes → additionally add @pytest.mark.slow
```

### Step 3 — Choose the test file

`IbToolPartion.py` (excluding `siedgr()`'s real pipeline) → `test_ibtoolpartion.py`. The real `siedgr()` pipeline → `test_siedgr_integration.py`. The dialog → `test_IbToolPartion_dialog.py`. If none fit, create `test_{module_name}.py` following the class structure in `ai/core/testing-rules.md`.

### Step 4 — Mandatory geometry checks

Every test for a function that returns a `QgsVectorLayer` must include:

```python
assert result_layer is not None
assert result_layer.featureCount() > 0          # or == expected_count
for feat in result_layer.getFeatures():
    geom = feat.geometry()
    assert not geom.isNull(),    "Geometry must not be null"
    assert not geom.isEmpty(),   "Geometry must not be empty"
    assert geom.isGeosValid(),   "Geometry must be GEOS-valid"
```

### Step 5 — Write a one-line docstring

Every test method must have a docstring in the imperative mood describing what behavior it verifies:

```python
def test_single_building(self, plugin, tmp_path):
    """siedgr() completes and produces a valid partition for a single building."""
```

---

## Gap Analysis and Prioritized Backlog

### Priority 1 — Small effort, high impact

| Gap | Action |
|---|---|
| Full `run()` success path untested | Add a unit test that configures the mock dialog with valid paths/`cell_size`, stubs `siedgr()`, and asserts the success `pushMessage` call |
| No `@pytest.mark.performance` test for `siedgr()` at scale | Add a `performance` + `slow` test with 50+ buildings, asserting it completes within a stated time budget |

### Priority 2 — Larger effort, lower urgency

| Gap | Action |
|---|---|
| `select_input_file`/`select_output_file` `QFileDialog` interaction untested | Mock `QFileDialog.getOpenFileName`/`getSaveFileName` and assert the dialog's `Input_HU`/`output_file` text fields are updated |
| `HU_Button`/`Output_Button` signal wiring in `run()` untested | Requires a live Qt event loop; cover via the same `get_qgis_app()` pattern used in `test_IbToolPartion_dialog.py` |

---

## Justified Exclusions

Documented decisions that **are not gaps** — known exclusions with stated reasons.

| Module / function | Reason for exclusion |
|---|---|
| `resources.py` | Generated by the Qt resource compiler (`pyrcc5`/`compile.bat`), not hand-written. |
| `Partitioning.pyt` | An ArcGIS Toolbox shipped alongside the QGIS plugin in the same repository; not part of the QGIS plugin runtime and excluded from `.coveragerc`. |
| `__init__.py` `classFactory()` | Requires a live `iface` object provided by the running QGIS application. Covered indirectly by the `test_init.py` metadata smoke test and the Docker CI run. |

---

## CI/CD

For the full CI/CD pipeline description and Docker environment setup, see [docs/contributing.md](contributing.md).

Quick reference for common test runs:

```bash
# Unit tests only (no QGIS Processing required)
pytest test/ -m "unit" -v

# Skip slow tests
pytest test/ -m "not slow" -v

# Full run (requires Docker or local QGIS)
docker run --rm -v $(pwd):/plugins/ibtoolpartion qgis-plugin-test

# Coverage report
pytest test/ --cov --cov-report=html

# Single module
pytest test/test_siedgr_integration.py -v
```

---

## Related Files

| File | Content |
|------|---------|
| [`docs/contributing.md`](contributing.md) | CI/CD pipeline, Docker environment, code linting |
| [`ai/core/testing-rules.md`](../ai/core/testing-rules.md) | Tactical rules: geometry checks, test structure, framework conventions |
| [`docs/Testplan-data_wizard-ibtoolpartion.md`](Testplan-data_wizard-ibtoolpartion.md) | Implementation plan this document and the current test suite were built from |
