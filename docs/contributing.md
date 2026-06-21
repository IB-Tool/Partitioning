# Contributing & Development

This document covers the development setup, CI/CD pipeline, test structure, and code quality tooling for IB-Tool (Partitioning).

---

## Continuous Integration with GitHub Actions

The project uses two GitHub Actions workflows:

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **CI** | `.github/workflows/ci.yml` | push to `master`/`main`, PRs | Docker-based tests + Codecov coverage |
| **QGIS Plugin CI** | `.github/workflows/qgis-plugin-ci.yml` | push to `master`/`main`, PRs | Lint, security scan, plugin structure validation |

---

## Workflow 1 — CI (Docker-based tests)

Runs the full test suite inside a Docker container with a real QGIS environment.

Steps:
1. Checks out the repository
2. Builds the Docker image from `Dockerfile` (must be provided at the repo root)
3. Runs the test suite inside the container with coverage reporting
4. Strips container-absolute paths from `coverage.xml`
5. Uploads the coverage report to Codecov

See `.github/workflows/ci.yml` for the full workflow definition and `IB-Tool-3` for a reference `Dockerfile`.

### Coverage Reporting

Test coverage is measured with `pytest-cov` and uploaded to [Codecov](https://codecov.io) on every CI run. The `coverage.xml` file is written by the container into the volume-mounted workspace. Container-absolute paths (`/plugins/ibtoolpartion/`) are stripped before upload so Codecov can map lines back to the repository.

### Local Development with Docker

```bash
# Build the Docker image
docker build -t qgis-plugin-test .
# Run tests
docker run --rm -v $(pwd):/plugins/ibtoolpartion qgis-plugin-test
# Interactive shell inside the container
docker run --rm -it qgis-plugin-test /bin/bash
```

---

## Workflow 2 — QGIS Plugin CI (linting & validation)

Runs static analysis without Docker — suitable for quick feedback on every push.

Steps:
1. **Plugin validator** (`ci/qgis_plugin_validate.py --auto`): checks folder name, required files (`metadata.txt`, `__init__.py`, `LICENSE`), and all required metadata keys.
2. **Flake8**: PEP 8 style checks.
3. **Bandit**: Security scan (medium severity and above).
4. **detect-secrets**: Scans for accidentally committed credentials.

Run locally:

```bash
pip install flake8 bandit detect-secrets
python ci/qgis_plugin_validate.py --auto
flake8 .
bandit -r . -ll
detect-secrets scan --force-use-all-plugins --exclude-files 'Test_data/.*'
```

---

## Code Quality Standards

| Tool | Purpose | Config |
|------|---------|--------|
| `flake8` | Style (PEP 8) | `.flake8` or `setup.cfg` |
| `bandit` | Security | `.bandit` |
| `pylint` | Comprehensive linting | `pylintrc` |
| `pytest` | Unit & integration tests | `pytest.ini` |
| `detect-secrets` | Credential scanning | — |

---

## Testing

Tests live in `test/`. Run them with:

```bash
# All tests (requires QGIS environment)
pytest test/ -v

# Unit tests only (no QGIS required)
pytest test/ -v -m unit
```

### Test tiers

| Marker | When to use |
|--------|-------------|
| `@pytest.mark.unit` | No `processing.run()` calls — fast, no QGIS needed |
| `@pytest.mark.integration` | Calls `processing.run()` — requires QGIS |
| `@pytest.mark.edge_case` | Boundary / degenerate inputs |
| `@pytest.mark.slow` | Runtime > 1 s or large synthetic datasets |

See `ai/core/testing-rules.md` for full testing conventions.

---

## AI Rules

The `ai/` directory contains rules and task templates for AI-assisted development:

| Path | Content |
|------|---------|
| `ai/core/` | Architecture guidelines, naming conventions, testing rules, QGIS API rules, debug mode, constraints, release conventions |
| `ai/tasks/` | Task templates: bugfix, refactor, new feature, QGIS processing |
| `ai/domain/` | Domain knowledge specific to this plugin |

---

## Related Files

| File | Content |
|------|---------|
| [`docs/CHANGELOG.md`](CHANGELOG.md) | Version history |
| [`ai/core/testing-rules.md`](../ai/core/testing-rules.md) | Test conventions |
| [`ai/core/constraints.md`](../ai/core/constraints.md) | Language and code constraints |
| [`ci/qgis_plugin_validate.py`](../ci/qgis_plugin_validate.py) | Plugin structure validator |
