-- Title: Quality grade count by project
-- Description: Counts observations by quality grade and shows each grade as a percentage of the project total.

SELECT
    project_alias,
    quality_grade,
    COUNT(*) AS observation_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY project_alias),
        2
    ) AS project_percentage
FROM observations
GROUP BY
    project_alias,
    quality_grade
ORDER BY
    project_alias,
    observation_count DESC;
