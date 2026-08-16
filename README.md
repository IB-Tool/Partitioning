# IB-Tool (Partitioning) — QGIS Plugin

[![CI](https://github.com/IB-Tool/Partitioning/actions/workflows/ci.yml/badge.svg)](https://github.com/IB-Tool/Partitioning/actions/workflows/ci.yml)
[![QGIS Plugin CI](https://github.com/IB-Tool/Partitioning/actions/workflows/qgis-plugin-ci.yml/badge.svg)](https://github.com/IB-Tool/Partitioning/actions/workflows/qgis-plugin-ci.yml)
[![License: GPL-2.0-or-later](https://img.shields.io/badge/License-GPL--2.0--or--later-blue.svg)](LICENSE)

A QGIS plugin that delineates settlement boundaries by partitioning spatial datasets based on building footprints.

This is a companion plugin to **[IB-Tool 3](https://github.com/IB-Tool/IB-Tool-3)**:
its output (a `PART_<id>` polygon layer) is the **Partitions** input IB-Tool 3
expects — see IB-Tool 3's
[`docs/input-data.md` → Part](https://github.com/IB-Tool/IB-Tool-3/blob/master/docs/input-data.md#part--partitioning)
and
[`docs/quickstart.md`](https://github.com/IB-Tool/IB-Tool-3/blob/master/docs/quickstart.md)
for how it fits into IB-Tool 3's own workflow.

IBTool needs four more input layers. Its sibling plugin
**[Data Wizard](https://github.com/IB-Tool/data_wizard)** produces the
`HU` / `RN` / `Aux` layers from raw ATKIS Basis-DLM data — the building
footprints it outputs can be fed straight into this plugin as input.

---

## What it does

The plugin generates partition polygons from building footprint data. The algorithm uses kernel density estimation on building centroids to identify settlement clusters, then derives partition boundaries via Voronoi tessellation and line processing.

**Processing pipeline:**

1. Building footprints → centroids
2. Kernel density raster (heatmap) from centroids
3. Raster → point grid
4. Voronoi polygons from point grid
5. Polygon to lines → explode line segments
6. Remove line segments within dense cluster areas
7. Polygonize remaining lines → partition polygons
8. Add `NAME` field (`PART_<id>`)

The result is a set of polygons that partition the study area into settlement units, each named `PART_<id>`.

---

## Requirements

- QGIS 3.0 or later
- Python 3.x (bundled with QGIS)
- No external Python packages required — all processing uses QGIS native algorithms

---

## Installation

### From ZIP (manual)

1. Download or clone this repository
2. Open QGIS → **Plugins** → **Manage and Install Plugins** → **Install from ZIP**
3. Select the `.zip` file and click **Install Plugin**

### From source (development)

Copy or symlink the `ibtoolpartion/` directory into your QGIS plugin folder:

| Platform | Plugin folder |
|----------|---------------|
| Windows  | `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` |
| Linux    | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |
| macOS    | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/` |

Then activate the plugin in QGIS via **Plugins** → **Manage and Install Plugins**.

---

## Usage

1. Open QGIS and activate the plugin
2. Click the **IB-Tool (Partitioning)** icon in the toolbar or use the **Plugins** menu
3. In the dialog, set:
   - **Building footprints** — polygon layer (`.shp` or `.gpkg`)
   - **Cell size (metres)** — raster resolution and density radius (default: `150`)
   - **Output file** — destination for the partition polygon layer (`.shp` or `.gpkg`)
4. Click **OK** — the output layer is written to the specified file

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Building footprints | Polygon layer | — | Input building footprint features |
| Cell size (metres) | Integer | `150` | Raster cell size; controls density estimation radius (`2 × cell_size`) |
| Output file | File path | — | Output partition polygon layer (`.shp` or `.gpkg`) |

---

## Development

### Setup

```bash
git clone <repo-url>
cd ibtoolpartion
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install flake8 bandit detect-secrets pylint pytest pytest-cov
```

### Run tests

```bash
# All tests (requires a running QGIS environment)
pytest test/ -v

# Unit tests only (no QGIS required)
pytest test/ -v -m unit
```

### Run tests with Docker

```bash
docker build -t qgis-plugin-test .
docker run --rm -v $(pwd):/plugins/ibtoolpartion qgis-plugin-test
```

### Build a release ZIP

```bash
python scripts/create_release_zip.py
```

Produces `dist/ibtoolpartion.<version>.zip`. See
[`docs/contributing.md` → Release Process](docs/contributing.md#release-process)
for the full checklist.

### Static analysis

```bash
python ci/qgis_plugin_validate.py --auto
flake8 .
bandit -r . -ll
detect-secrets scan --force-use-all-plugins
```

### Test markers

| Marker | When to use |
|--------|-------------|
| `@pytest.mark.unit` | No `processing.run()` calls — no QGIS required |
| `@pytest.mark.integration` | Calls `processing.run()` — requires QGIS |
| `@pytest.mark.edge_case` | Boundary or degenerate inputs |
| `@pytest.mark.slow` | Runtime > 1 s or large datasets |

---

## CI / CD

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push to `master`/`main`, PRs | Docker-based tests + Codecov coverage |
| `qgis-plugin-ci.yml` | Push to `master`/`main`, PRs | Lint (flake8), security scan (bandit), plugin validation |

---

## Citation

This plugin is based on the following published toolset:

> Oliver Harig (2021). *Toolset for the delineation of settlements on the basis building footprints, road network and land use data* (v1.0). https://doi.org/10.26084/IOERFDZ-SOFT-001

---

## License

This plugin is released under the **GNU General Public License v2** (or later).
See [`LICENSE`](LICENSE) for the full license text.

---

## Author

Oliver Harig — ottmar.hittzfeld@web.de
