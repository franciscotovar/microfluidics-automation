# Microfluidics Automation

Research software for microfluidic instrument control and hydraulic characterization, independent of coatl-cad.

## Start here

Open `notebooks/SPS01_BBRES_Research_Workflow.ipynb` to analyse LabSmith SPS01/BBRES pressure traces, hydraulic resistance, damping, dead volume, and collection windows.

The notebook includes illustrative parameters. Calibrate pressure targets, sensor mappings, flow rates and tubing dimensions before interpreting measurements.

## Layout

- `notebooks/`: experimental analyses
- `labsmith/scripts/`: validated uProcess scripts (future)
- `labsmith/python/`: LabSmith Python interface (future)
- `tecan/python/`: Cavro drivers and tests (future)
- `data/examples/`: reviewed sample datasets
- `data/raw/`: local raw data, excluded from Git
- `src/microfluidics_automation/`: reusable Python modules (future)
- `docs/`: experimental notes

## Data

Do not commit unreviewed raw measurements or confidential material. Add only curated example data with documented experimental conditions.
