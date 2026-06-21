# Changelog

All notable changes to IB-Tool (Partitioning) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Unreleased

---

## 0.1.0 — 2026-06-21

### Added
- Initial project structure: plugin entry point, dialog, UI, i18n, test scaffold.
- AI rules (`ai/core/`, `ai/tasks/`): architecture guidelines, naming conventions, testing rules, QGIS API rules, debug mode, constraints, release conventions, and task templates (bugfix, refactor, new feature, QGIS processing).
- CI (`ci/qgis_plugin_validate.py`): QGIS plugin structure and metadata validator.
- GitHub Actions workflows: Docker-based test runner (`ci.yml`), linter/security scanner (`qgis-plugin-ci.yml`).
- Claude commands (`.claude/commands/`): `write-docs`, `write-tests`, `sync-docs`.
