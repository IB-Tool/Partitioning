# IB-Tool (Partitioning) — QGIS Plugin

A QGIS plugin that delineates settlement boundaries by partitioning spatial datasets based on building footprints.

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

### Static analysis

```bash
python ci/qgis_plugin_validate.py --auto
flake8 .
bandit -r . -ll
detect-secrets scan --force-use-all-plugins --exclude-files 'Test_data/.*'
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
See `Test_data/LICENSE.txt` for the license text of the bundled test data.

---

## Author

Oliver Harig — ottmar.hittzfeld@web.de
