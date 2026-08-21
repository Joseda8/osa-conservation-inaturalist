# OSA Conservation - iNaturalist Analyzer
This project provides tools to analyze OSA Conservation data from iNaturalist and other sources.

Raw observation data for these projects is downloaded:

- `obs`: The OSA Biodiversity Survey.
- `abs`: The AmistOSA Biodiversity Survey.

## Pipeline
The pipeline is organized as reusable steps.

### Download raw data
Downloads raw iNaturalist API pages for each configured project. By default, downloads are incremental and include observations updated since the previous local midnight.

Raw data is stored by project and download date:

```text
data/raw/<project_alias>/<YYYYMMDD>/<project_alias>_<YYYYMMDD>_page_<NUMBER>.json
```

Example:

```text
data/raw/obs/20260606/obs_20260606_page_000001.json
```

The page number padding is computed from the total results reported by iNaturalist and the requested batch size.

### Initialize database
Applies the PostgreSQL 1.0 schema at `db/migrations/0001_initial_schema.sql`. Apply it once to a new, empty database before loading data.

### Load raw data to database
Loads downloaded observation pages and aggregate trend files into PostgreSQL.

### Reconcile project observations
Checks current iNaturalist project membership and deletes local normalized rows for observations that no longer belong to the configured projects. Raw JSON page snapshots are kept unchanged.

### Enrich taxonomy
Completes the `taxa` table with metadata for every ID referenced by stored taxon lineages. Missing mode requests only absent lineage nodes. Full mode refreshes all stored taxa and then completes any newly discovered lineage nodes.

### Download trends
Downloads compact observed-date monthly aggregate trends for `obs`, `abs`, and Costa Rica into raw JSON files. This includes observation histograms, species counts, and iconic taxa species counts. This uses iNaturalist aggregate endpoints instead of downloading all Costa Rica observations.

Trend data is stored by download date, region, and metric:

```text
data/raw/trends/<YYYYMMDD>/trends_<YYYYMMDD>_<region>_<metric>.json
```

Run `load-raw-data-to-db` after downloading trends to load those files into PostgreSQL.

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

Run the complete update for one calendar month:

```bash
PYTHONPATH=src python3 src/main.py --pipeline monthly-update --year 2026 --month 7
```

This downloads the selected month for observations and trends, loads only the files created by the command, reconciles project membership, and enriches missing taxonomy. Initialize the database separately with `--steps migrate-db` before the first run.

Run the initial historical import before monthly updates:

```bash
PYTHONPATH=src python3 src/main.py --pipeline historical-load
```

This downloads all available project observations and trend history, then loads, reconciles, and enriches the resulting data.

Run selected steps:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data
```

Run the initial database analysis and upload its CSV export to Google Drive:

```bash
# Save the OAuth desktop client JSON at .secrets/google-oauth-client.json.
PYTHONPATH=src python3 src/main.py --steps analyze-and-upload-to-drive
```

The first run opens a browser for the selected Google user to authorize the pipeline. Its refresh token is saved at `.secrets/google-oauth-token.json`. The step runs `SELECT * FROM observations LIMIT 5;`, writes the result to an in-memory CSV with headers, and creates or replaces `observations.csv` in the configured Google Drive folder. Set `GOOGLE_DRIVE_UPLOAD_FOLDER_ID` in the ignored `.env` file to the ID of OSA's `processed-data` folder. Never commit either OAuth JSON file. Set `GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH` or `GOOGLE_DRIVE_OAUTH_TOKEN_PATH` to use different local paths; set `GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME` to override the file name.

## GitHub Actions

The manual **Refresh GitHub Pages** workflow downloads `observations.csv`, builds the React site, and deploys it to GitHub Pages. Before running it, add `GOOGLE_DRIVE_UPLOAD_FOLDER_ID` as an Actions variable and the complete OAuth token JSON as an Actions secret named `GOOGLE_DRIVE_OAUTH_TOKEN_JSON`. The deployed CSV data is public, so it must contain only information suitable for public release.

Run a full raw data download:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --download-mode full
```

Run an incremental download with an explicit local cutoff:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --download-mode incremental --updated-since 2026-06-06T00:00:00-06:00
```

Download observations observed within an inclusive date range:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --download-mode full --observed-date-start 2026-07-01 --observed-date-end 2026-07-31
```

Initialize a new database:

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

Initialize a new database and load raw data:

```bash
PYTHONPATH=src python3 src/main.py --steps migrate-db
PYTHONPATH=src python3 src/main.py --steps load-raw-data-to-db
```

Delete normalized observations that no longer belong to the configured iNaturalist projects:

```bash
PYTHONPATH=src python3 src/main.py --steps reconcile-project-observations
```

Complete missing taxonomy lineage nodes:

```bash
PYTHONPATH=src python3 src/main.py --steps enrich-taxonomy
```

Refresh all stored taxa and complete their lineages:

```bash
PYTHONPATH=src python3 src/main.py --steps enrich-taxonomy --taxonomy-mode full
```

Download and store historical monthly aggregate trends:

```bash
PYTHONPATH=src python3 src/main.py --steps download-trends --trend-mode historical
```

Download and store monthly aggregate trends since a completed month:

```bash
PYTHONPATH=src python3 src/main.py --steps download-trends --trend-mode since --trend-year 2026 --trend-month 1
```

Download and load the complete July 2026 snapshot, then reconcile project membership and enrich taxonomy. Replace `20260802` with the date on which the command is run:

```bash
PYTHONPATH=src python3 src/main.py --steps migrate-db download-raw-data download-trends load-raw-data-to-db reconcile-project-observations enrich-taxonomy --download-mode full --observed-date-start 2026-07-01 --observed-date-end 2026-07-31 --trend-mode since --trend-year 2026 --trend-month 7 --trend-end-year 2026 --trend-end-month 7 --load-date 20260802
```

For normal use, prefer the shorter `--pipeline monthly-update` command above.

Run the download step more gently for large projects:

```bash
PYTHONPATH=src python3 src/main.py --steps download-raw-data --per-page 25 --request-cooldown 1.1 --failure-cooldown 60
```
