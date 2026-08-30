-- Counts observations stored for each OSA project and both projects combined.

WITH project_observations AS (
    SELECT
        project_alias,
        observation_id
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
),
project_counts AS (
    SELECT
        project_alias,
        COUNT(*) AS observation_count
    FROM project_observations
    GROUP BY project_alias
),
aggregated_count AS (
    SELECT
        'aggregated'::TEXT AS project_alias,
        COUNT(DISTINCT observation_id) AS observation_count
    FROM project_observations
)
SELECT
    project_alias,
    observation_count
FROM project_counts
UNION ALL
SELECT
    project_alias,
    observation_count
FROM aggregated_count
ORDER BY project_alias;
