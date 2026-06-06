# OSA Conservation - iNaturalist Analyzer
This project provides tools to analyze OSA Conversation data from iNaturalists and other sources.

## Projects
The default pipeline downloads raw observation data for:

- `obs`: The OSA Biodiversity Survey.
- `abs`: The AmistOSA Biodiversity Survey.

## Pipeline
The pipeline is organized as reusable steps.

### Download raw data
Downloads raw iNaturalist API pages for each configured project.

Raw data is stored by project and download date:

```text
data/<project_alias>/<YYYYMMDD>/raw_data/<project_alias>_<YYYYMMDD>_page_<NUMBER>.json
```

Example:

```text
data/obs/20260606/raw_data/obs_20260606_page_000001.json
```

The page number padding is computed from the total results reported by iNaturalist and the requested batch size.

## Usage
List available steps:

```bash
PYTHONPATH=src python3 src/main.py --list-steps
```

Run all configured steps:

```bash
PYTHONPATH=src python3 src/main.py
```

Run selected steps:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data
```

Run the download step more gently for large projects:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --per-page 25 --request-cooldown 1.1 --failure-cooldown 60
```
