---
description: Use this skill when the user wants the project documentation (docs/ folder and README.md) to be audited and harmonized — for example "docs konsistent machen", "Doku abstimmen", "Redundanzen entfernen", "einheitlichen Stil herstellen", "sync-docs". Invoke whenever documentation consistency across the whole project is the goal.
---

# /sync-docs — Audit and Harmonize IbToolPartion Documentation

Audit and harmonize all project documentation: **docs/**, **README.md**.

Follow these steps in order. Do not skip any step.

---

## Step 1 — Read all documentation files

Read every file in `docs/` and `README.md` completely before making any changes.

Also read `CLAUDE.md` (if present) to understand which files are listed in documentation tables.

---

## Step 2 — Audit: identify all issues

Before touching any file, produce a written audit covering all four issue categories below.

### 2.1 Redundancies

Flag every piece of content that appears in more than one file. For each redundancy: decide which file is the **canonical home** and which file should only carry a one-line cross-reference.

**Canon assignment rules:**

| Topic | Canonical file |
|---|---|
| Input layer specs, field requirements, validation checks | `docs/input-data.md` |
| Processing parameters, defaults | `docs/parameterization.md` |
| CI/CD workflows | `docs/contributing.md` |
| Test taxonomy, coverage targets | `docs/test-strategy.md` |
| Logging system, error categories, debug mode | `docs/error-handling.md` |
| Code structure, entry points, package layout | `docs/plugin-architecture.md` |
| Full algorithmic pipeline | `docs/how-it-works.md` |
| Brief feature overview, installation, usage quick-start | `README.md` |

### 2.2 Style inconsistencies

Check each file against the unified style standard (see Step 4). Flag every deviation:
- Numbered section headings → must be unnumbered
- Missing `---` horizontal rules between H2 sections
- Missing introductory paragraph
- Missing `## Related Files` section at the end
- German prose (UI labels in backticks are allowed)

### 2.3 Structural gaps

Check that every cross-reference link points to a file that exists.

### 2.4 Documents to split or merge

Assess whether any document is too broad or too thin.

---

## Step 3 — Produce change plan

After the audit, list every planned change as a numbered action before starting any edits.

---

## Step 4 — Apply changes: enforce unified style standard

#### Document structure (required for all files except README.md)

```markdown
# Document Title

One introductory paragraph.

---

## Section Heading

Content.

---

## Related Files

| File | Content |
|------|---------|
| [`path/to/file.md`](path/to/file.md) | What it covers |
```

#### Rules
- `#` — document title (exactly one per file)
- `##` — major sections; **never** number them
- `---` separator between every pair of H2 sections
- Prose: **English throughout**; German only for direct QGIS UI labels in backticks
- Never reproduce a table that belongs to another document — cross-reference it instead

---

## Step 5 — Output

Report:
1. **Redundancies removed** — list each file + section replaced by a cross-reference
2. **Style changes** — list files where headings, separators, intro paragraphs, Related Files were fixed
3. **Splits or merges** — describe any structural changes
4. **Open questions** — any content where canonical home was ambiguous
