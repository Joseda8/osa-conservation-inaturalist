# OSA Conservation - iNaturalist Analyzer
This project provides tools to analyze OSA Conversation data from iNaturalists and other sources.

## Projects
The default pipeline downloads raw observation data for:

- `obs`: The OSA Biodiversity Survey.
- `abs`: The AmistOSA Biodiversity Survey.

## Pipeline
The pipeline is organized as reusable steps.

### Download raw data
Downloads raw iNaturalist API pages for each configured project. By default, downloads are incremental and include observations updated since the previous local midnight.

Raw data is stored by project and download date:

```text
data/<project_alias>/<YYYYMMDD>/raw_data/<project_alias>_<YYYYMMDD>_page_<NUMBER>.json
```

Example:

```text
data/obs/20260606/raw_data/obs_20260606_page_000001.json
```

The page number padding is computed from the total results reported by iNaturalist and the requested batch size.

### Migrate database
Applies pending PostgreSQL migrations from `db/migrations`.

### Load raw data to database
Loads downloaded raw JSON files into PostgreSQL.

### Reconcile project observations
Checks current iNaturalist project membership and deletes local normalized rows for observations that no longer belong to the configured projects. Raw JSON page snapshots are kept unchanged.

### Download trends
Downloads compact observed-date monthly aggregate observation trends for `obs`, `abs`, and Costa Rica into PostgreSQL. This uses iNaturalist aggregate endpoints instead of downloading all Costa Rica observations.

The trend step can download all historical monthly buckets, or update from a completed starting month through the most recent completed month.

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

Run a full raw data download:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --download-mode full
```

Run an incremental download with an explicit local cutoff:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --download-mode incremental --updated-since 2026-06-06T00:00:00-06:00
```

Run database migrations:

```bash
PYTHONPATH=src python3 src/main.py --steps migrate-db
```

Load raw data into PostgreSQL:

```bash
PYTHONPATH=src python3 src/main.py --steps load-raw-data-to-db
```

Load raw data for one snapshot date:

```bash
PYTHONPATH=src python3 src/main.py --steps load-raw-data-to-db --load-date 20260607
```

Run migrations and then load raw data:

```bash
PYTHONPATH=src python3 src/main.py --steps migrate-db load-raw-data-to-db
```

Delete normalized observations that no longer belong to the configured iNaturalist projects:

```bash
PYTHONPATH=src python3 src/main.py --steps reconcile-project-observations
```

Download historical monthly aggregate trends:

```bash
PYTHONPATH=src python3 src/main.py --steps migrate-db download-trends --trend-mode historical
```

Download monthly aggregate trends since a completed month:

```bash
PYTHONPATH=src python3 src/main.py --steps migrate-db download-trends --trend-mode since --trend-year 2026 --trend-month 1
```

Run the download step more gently for large projects:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --per-page 25 --request-cooldown 1.1 --failure-cooldown 60
```
