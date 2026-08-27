-- Counts observations by their Costa Rica observed date for each OSA project and both combined.

WITH dated_project_observations AS (
    SELECT
        project_alias,
        observation_id,
        (observed_on AT TIME ZONE 'America/Costa_Rica')::DATE AS observed_date
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
        AND observed_on IS NOT NULL
),
project_counts AS (
    SELECT
        project_alias,
        observed_date,
        COUNT(*) AS observation_count
    FROM dated_project_observations
    GROUP BY
        project_alias,
        observed_date
),
aggregated_counts AS (
    SELECT
        'aggregated'::TEXT AS project_alias,
        observed_date,
        COUNT(DISTINCT observation_id) AS observation_count
    FROM dated_project_observations
    GROUP BY observed_date
)
SELECT
    project_alias,
    observed_date,
    observation_count
FROM project_counts
UNION ALL
SELECT
    project_alias,
    observed_date,
    observation_count
FROM aggregated_counts
ORDER BY
    observed_date,
    project_alias;
