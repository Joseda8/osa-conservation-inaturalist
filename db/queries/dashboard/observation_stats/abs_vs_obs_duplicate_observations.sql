-- Lists iNaturalist observations included in both OSA projects.

WITH duplicate_observations AS (
    SELECT observation_id
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
    GROUP BY observation_id
    HAVING COUNT(DISTINCT project_alias) = 2
),
numbered_duplicate_observations AS (
    SELECT
        observation_id,
        COUNT(*) OVER () AS duplicate_observation_count,
        ROW_NUMBER() OVER (ORDER BY observation_id) AS duplicate_observation_position
    FROM duplicate_observations
)
SELECT
    'aggregated'::TEXT AS project_alias,
    CASE WHEN duplicate_observation_position = 1 THEN duplicate_observation_count END AS duplicate_observation_count,
    observation_id
FROM numbered_duplicate_observations
ORDER BY observation_id;
