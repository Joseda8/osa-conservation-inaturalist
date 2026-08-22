-- Counts observations by quality grade for each OSA project.

SELECT
    project_alias,
    quality_grade,
    COUNT(*) AS observation_count
FROM observations
WHERE project_alias IN ('abs', 'obs')
GROUP BY
    project_alias,
    quality_grade
ORDER BY
    project_alias,
    quality_grade;
