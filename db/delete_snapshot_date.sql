-- Title: Delete snapshot date from database
-- Description: Deletes observations and project-scoped child rows for one download_date.
--
-- Usage:
--   docker compose exec -T postgres psql -U osa -d osa_inaturalist \
--     -v snapshot_date='2026-06-11' \
--     -f db/delete_snapshot_date.sql

BEGIN;

CREATE TEMP TABLE target_snapshot_observations ON COMMIT DROP AS
SELECT
    project_alias,
    observation_id
FROM observations
WHERE download_date = DATE :'snapshot_date';

WITH deleted_photos AS (
    DELETE FROM observation_photos AS photos
    USING target_snapshot_observations AS targets
    WHERE photos.project_alias = targets.project_alias
        AND photos.observation_id = targets.observation_id
    RETURNING photos.project_alias
),
deleted_observations AS (
    DELETE FROM observations AS observation_rows
    USING target_snapshot_observations AS targets
    WHERE observation_rows.project_alias = targets.project_alias
        AND observation_rows.observation_id = targets.observation_id
    RETURNING observation_rows.project_alias
),
deleted_orphan_observers AS (
    DELETE FROM observers AS observer_rows
    WHERE NOT EXISTS (
        SELECT 1
        FROM observations AS observation_rows
        WHERE observation_rows.observer_id = observer_rows.observer_id
    )
    RETURNING observer_id
),
deleted_orphan_taxa AS (
    DELETE FROM taxa AS taxon_rows
    WHERE NOT EXISTS (
        SELECT 1
        FROM observations AS observation_rows
        WHERE observation_rows.taxon_id = taxon_rows.taxon_id
    )
    RETURNING taxon_id
)
SELECT 'observation_photos' AS deleted_from, project_alias, COUNT(*) AS rows
FROM deleted_photos
GROUP BY project_alias
UNION ALL
SELECT 'observations', project_alias, COUNT(*)
FROM deleted_observations
GROUP BY project_alias
UNION ALL
SELECT 'orphan_observers', NULL, COUNT(*)
FROM deleted_orphan_observers
UNION ALL
SELECT 'orphan_taxa', NULL, COUNT(*)
FROM deleted_orphan_taxa
ORDER BY
    deleted_from,
    project_alias;

COMMIT;
