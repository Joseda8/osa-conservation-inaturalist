-- Counts observations by their Costa Rica observed date for each OSA project.

SELECT
    project_alias,
    (observed_on AT TIME ZONE 'America/Costa_Rica')::DATE AS observed_date,
    COUNT(*) AS observation_count
FROM observations
WHERE project_alias IN ('abs', 'obs')
    AND observed_on IS NOT NULL
GROUP BY
    project_alias,
    (observed_on AT TIME ZONE 'America/Costa_Rica')::DATE
ORDER BY
    observed_date,
    project_alias;
