# Changelog

All notable changes to IB-Tool (Partitioning) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Unreleased

### Added
- `Dockerfile` for Docker-based test execution (previously referenced by `ci.yml`/`docs/contributing.md` but missing).
- `scripts/create_release_zip.py` — release ZIP builder, mirroring IB-Tool 3's own script.
- Cross-links to IB-Tool 3's documentation (README, `docs/contributing.md`) describing this plugin's role as IB-Tool 3's Partitions input provider.

### Fixed
- `metadata.txt`: replaced placeholder `tracker`/`repository`/`homepage` URLs (`http://bugs`, `http://repo`, `http://homepage`) with the actual repository URLs; removed a stray unescaped line that was silently parsed as a bogus `category of the plugin` key; added a `changelog` entry (previously commented out).
- `README.md`: removed incorrect reference to a non-existent `Test_data/LICENSE.txt`; removed stale `Test_data/.*` exclude pattern from `detect-secrets` examples (no such directory exists in this repo).
- `.github/workflows/ci.yml`: removed the "Dockerfile missing, see IB-Tool 3" comment now that a `Dockerfile` exists here.

---

## 0.1.0 — 2026-06-21

### Added
- Initial project structure: plugin entry point, dialog, UI, i18n, test scaffold.
- AI rules (`ai/core/`, `ai/tasks/`): architecture guidelines, naming conventions, testing rules, QGIS API rules, debug mode, constraints, release conventions, and task templates (bugfix, refactor, new feature, QGIS processing).
- CI (`ci/qgis_plugin_validate.py`): QGIS plugin structure and metadata validator.
- GitHub Actions workflows: Docker-based test runner (`ci.yml`), linter/security scanner (`qgis-plugin-ci.yml`).
- Claude commands (`.claude/commands/`): `write-docs`, `write-tests`, `sync-docs`.
