# SPC CMM Suite

Windows-focused Tkinter desktop application for practical metrology workflows.

## What is in this build

### Main shell
- Left-side navigation for **SPC**, **CMM**, and **Quality** tool groups
- Top tab sets inside each section
- Logo support that automatically loads the existing `company-site/assets/img/logo.png` when available
- Clean placeholder badge fallback if the logo asset is unavailable

### SPC workbench
- Import **CSV** or **XLSX** datasets
- Re-use **CAD / CMM Compare** results directly for capability analysis
- Detect and offer selectable **numeric columns**
- Enter **LSL / USL** spec limits
- Apply simple data cleanup / manipulation on the chosen feature:
  - drop blanks / non-numeric values
  - minimum filter
  - maximum filter
- Calculate:
  - n
  - mean
  - sample standard deviation
  - population standard deviation
  - min / max
  - Cp / Cpk
  - Pp / Ppk
- Show:
  - histogram
  - run chart
  - first 100 filtered rows in a preview grid
  - notes showing how many rows were removed by filtering

### CMM tools
- **Angle → IJK** converter
  - XY and Z angle sliders
  - live direction cosine output
  - 3-decimal display
  - projected vector preview on axes
- **PRG editor**
  - open `.PRG`
  - edit freely
  - find next
  - replace current
  - replace all
  - save / save as
- **CAD / CMM Compare**
  - import CSV/XLSX nominal-vs-measured datasets
  - import CMM results from CSV/XLSX/TXT/TSV with auto-detected columns
  - choose feature label, nominal, and measured columns
  - calculate deviation and absolute deviation
  - apply symmetric tolerance (±) for PASS / FAIL classification
  - auto-use detected tolerance columns when present
  - optional FAIL-only filtering for triage
  - view deviation trend and measured-vs-nominal scatter plot
  - export compare results to CSV

### Quality section
- Placeholder tab ready for future FAIR, MSA, reporting, or NCR tools

## Project structure

- `src/main.py` — startup entry point
- `src/app.py` — desktop shell and navigation
- `src/spc_panel.py` — SPC import, filtering, metrics, plots, preview
- `src/analytics.py` — dataset loading and capability calculations
- `src/cmm_panel.py` — angle/vector tool and quality placeholder
- `src/compare_panel.py` — nominal-vs-measured compare workflow
- `src/cmm_import.py` — CMM results import and column auto-detection
- `src/prg_editor.py` — PC-DMIS PRG editor
- `src/shared_state.py` — cross-tool data handoff between compare and SPC
- `src/logo.py` — shared logo loading / fallback
- `samples/` — example data

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python src/main.py
```

## Smoke tests

### Syntax / import check
```powershell
Get-ChildItem src\*.py | ForEach-Object { python -m py_compile $_.FullName }
```

### Launch the UI
```powershell
python src/main.py
```

## Notes

- Capability indices are calculated only when **both** LSL and USL are supplied and USL > LSL.
- Cp/Cpk use **sample** standard deviation.
- Pp/Ppk use **population** standard deviation.
- This is intentionally a strong phase-1 desktop build; point-cloud vs STEP comparison will need additional CAD / geometry tooling later.
