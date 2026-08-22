-- Counts observations stored for each OSA project.

SELECT
    project_alias,
    COUNT(*) AS observation_count
FROM observations
WHERE project_alias IN ('abs', 'obs')
GROUP BY project_alias
ORDER BY project_alias;
