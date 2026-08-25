-- Lists iNaturalist observations included in both OSA projects.

WITH duplicate_observations AS (
    SELECT observation_id
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
    GROUP BY observation_id
    HAVING COUNT(DISTINCT project_alias) = 2
)
SELECT
    COUNT(*) OVER () AS duplicate_observation_count,
    observation_id
FROM duplicate_observations
ORDER BY observation_id;
