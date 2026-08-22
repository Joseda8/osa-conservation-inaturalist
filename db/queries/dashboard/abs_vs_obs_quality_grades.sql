-- Counts observations by quality grade for each OSA project.

SELECT
    project_alias,
    quality_grade,
    COUNT(*) AS observation_count,
    SUM(COUNT(*)) OVER () AS total_observation_count,
    SUM(COUNT(*)) OVER (PARTITION BY project_alias) AS project_total_observation_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY project_alias), 1) AS project_observation_percentage
FROM observations
WHERE project_alias IN ('abs', 'obs')
GROUP BY
    project_alias,
    quality_grade
ORDER BY
    project_alias,
    quality_grade;
