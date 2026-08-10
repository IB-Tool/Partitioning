#!/usr/bin/env python3
"""Create a QGIS plugin release ZIP.

Usage:
    python scripts/create_release_zip.py

Output:
    dist/ibtoolpartion.<version>.zip

The script reads the version from metadata.txt, collects all productive plugin
files (applying the exclusion list), and packages them under the folder name
ibtoolpartion/ inside the ZIP.

Run from the repository root.
"""
from __future__ import annotations

import configparser
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Exclusion rules
# ---------------------------------------------------------------------------

EXCLUDED_DIRS = {
    "test",
    "Testdaten",
    "ai",
    "ci",
    "docs",
    ".github",
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "dist",
    "venv",
    ".venv",
    "env",
    ".eggs",
    "logs",
    "scripts",
    "help",
    "build",
    "htmlcov",
    "workflows",
}

EXCLUDED_FILES = {
    "CLAUDE.md",
    "plugin_upload.py",
    "pytest.ini",
    "codecov.yml",
    "Dockerfile",
    "Makefile",
    "compile.bat",
    "pb_tool.cfg",
    "setup.cfg",
    "setup_qgis_path.py",
    "requirements-test.txt",
    "pylintrc",
    ".gitignore",
    ".gitattributes",
    ".secrets.baseline",
    ".flake8",
    ".bandit",
    ".DS_Store",
    "Thumbs.db",
    "Desktop.ini",
    "nul",
}

EXCLUDED_FILE_PATTERNS = (
    "- Kopie",
    "_kopie",
    "_original_backup",
)

EXCLUDED_FILE_PREFIXES = (
    "debug_",
)

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".iml",
    ".iws",
    ".ipr",
    ".egg-info",
    ".egg",
    ".so",
    ".log",
}


def is_excluded(rel: Path) -> bool:
    """Return True if the repo-relative path should be left out of the release ZIP.

    A path is excluded if any parent directory matches EXCLUDED_DIRS (or is
    hidden / an .egg-info dir), or if the filename itself matches one of the
    exact-name, prefix, substring, extension, or hidden-file exclusion rules.
    """
    parts = rel.parts

    # Any path component is an excluded directory
    for part in parts[:-1]:
        if part in EXCLUDED_DIRS or part.startswith(".") or part.endswith(".egg-info"):
            return True

    filename = parts[-1]
    suffix = Path(filename).suffix.lower()

    return (
        # Excluded by exact filename
        filename in EXCLUDED_FILES
        # Excluded by filename prefix (e.g. debug_*.py)
        or filename.startswith(EXCLUDED_FILE_PREFIXES)
        # Excluded by filename substring (e.g. backup/copy files)
        or any(pattern in filename for pattern in EXCLUDED_FILE_PATTERNS)
        # Excluded by extension
        or suffix in EXCLUDED_EXTENSIONS
        # Hidden files (dotfiles) other than those explicitly included
        or filename.startswith(".")
        # __pycache__ directories (caught above, but also as file path component)
        or "__pycache__" in parts
    )


def read_version(repo_root: Path) -> str:
    """Read the plugin version from the [general] section of metadata.txt."""
    meta_path = repo_root / "metadata.txt"
    if not meta_path.exists():
        raise FileNotFoundError(f"metadata.txt not found at {meta_path}")
    parser = configparser.ConfigParser()
    # metadata.txt has a [general] section
    parser.read(str(meta_path), encoding="utf-8")
    try:
        return parser["general"]["version"].strip()
    except KeyError as exc:
        raise ValueError("version key not found in metadata.txt [general]") from exc


def collect_files(repo_root: Path) -> list[Path]:
    """Return all repo-relative file paths that should ship in the release ZIP."""
    collected = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(repo_root)
        except ValueError:
            continue
        if not is_excluded(rel):
            collected.append(rel)
    return collected


def build_zip(repo_root: Path, files: list[Path], zip_path: Path, plugin_folder: str) -> None:
    """Write `files` (repo-relative paths) into a ZIP under `plugin_folder/`."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            arcname = f"{plugin_folder}/{rel.as_posix()}"
            zf.write(repo_root / rel, arcname)
            print(f"  + {arcname}")


def main() -> None:
    """Build the release ZIP for the plugin found next to this script."""
    repo_root = Path(__file__).resolve().parent.parent
    plugin_folder = repo_root.name  # ibtoolpartion

    version = read_version(repo_root)
    zip_name = f"{plugin_folder}.{version}.zip"
    zip_path = repo_root / "dist" / zip_name

    print(f"Plugin:  {plugin_folder}")
    print(f"Version: {version}")
    print(f"Output:  {zip_path}")
    print()

    files = collect_files(repo_root)
    print(f"Packaging {len(files)} files:")
    build_zip(repo_root, files, zip_path, plugin_folder)

    print()
    print(f"Created {zip_path}")


if __name__ == "__main__":
    main()
