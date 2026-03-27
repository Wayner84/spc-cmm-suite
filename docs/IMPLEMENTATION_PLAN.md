# Implementation Plan

## Product name
Working name: **SPC CMM Suite**

## Core goal
Create a Windows desktop tool for metrology/inspection work that covers:
- SPC/capability analysis
- practical CMM helper utilities
- PC-DMIS program editing
- longer-term CAD-vs-point-cloud deviation visualisation

## Architecture

### UI
- Python 3.x
- Tkinter + ttk Notebook for top-level tabs
- Matplotlib embedding for SPC charts

### Data and analysis
- pandas for import/manipulation
- numpy for calculations
- scipy/statsmodels where useful for stats
- openpyxl for xlsx handling

### 3D / geometry
Phase 1:
- keep angle/IJK visual simple with a lightweight embedded matplotlib 3D axis

Phase 3:
- evaluate:
  - pythonOCC / OCP for STEP loading
  - trimesh / pyvista / vtk for visualisation and nearest-surface style colouring

## Planned modules

### `src/main.py`
Application entry point.

### `src/app.py`
Main Tkinter application shell.

### `src/spc/`
- importers
- model
- stats/capability calculations
- plotting helpers
- SPC tab UI

### `src/cmm/`
- angle to IJK converter logic
- vector visualiser
- point cloud import scaffold
- STEP compare scaffold
- PRG editor tab/tooling

## Phase 1 deliverables
1. App shell with tabs
2. SPC import from CSV/XLSX
3. column selection UI
4. spec limit entry
5. capability calculations:
   - n
   - mean
   - min/max
   - std dev
   - Cp/Cpk
   - Pp/Ppk
6. histogram and run chart
7. angle → IJK converter
8. basic 3D vector visual
9. PRG editor open/edit/find/replace/save

## Open questions
- Preferred point cloud input format from PC-DMIS:
  - CSV?
  - TXT?
  - XYZ?
  - ASCII point list?
- Which SPC chart types matter most first:
  - individuals / moving range?
  - Xbar-R?
  - Xbar-S?
- Does Ween want project/session save files early?

## Practical recommendation
Build the app so the **first usable version** is focused on:
- SPC capability work
- angle/IJK helper
- PRG editing

Then bolt in CAD-vs-point-cloud compare once we’ve chosen the geometry stack carefully.
