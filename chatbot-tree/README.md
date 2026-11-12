# Guided chat tree (prototype) — شجرة الشات الموجّه

Status: PROTOTYPE / owner review only. Nothing here is wired to production, n8n, the website, or any live sheet.

## Files
- `tree.json` — the question tree (49 nodes, AR/EN/FR). Data only; the widget reads this file.
- `tree_report.md` — what was excluded, which texts are composed (need owner approval), language gaps, content not found in the KB.
- `build_tree.py` — regenerates `tree.json` from the approved KB workbook (active rows only; excluded records listed in the script).
- `prototype_template.html` + `build_prototype.py` — builds the browsable review prototype.

## How to change the tree
1. Answers/prices/policies: edit the approved KB sheet, export the workbook, then
   `python3 -I build_tree.py <kb.xlsx> .` — integrity checks fail the build on missing parents/targets, orphans, or excluded records.
2. Structure/ordering/labels: edit `build_tree.py` (menu order in `MAIN`, labels in `add(...)`), or ask Claude to make the change.
3. Rebuild the prototype: `python3 -I build_prototype.py tree.json prototype_template.html prototype.html`.
4. Open a PR. Owner reviews the prototype before merge. Merge does not deploy anything.

## Rules carried over from the project
- Approved KB wording is used verbatim; composed text is flagged `origin: composed` and needs owner approval.
- Registration validation mirrors the locked R1 validator; the server remains the authority. The prototype never sends data.
- The KB snapshot is 2026-08-18; the live sheet changed after 2026-09-17 and must be re-checked before release.
