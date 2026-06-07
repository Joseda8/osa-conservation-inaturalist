-- Title: Quality grade count
-- Description: Counts observations by quality grade and shows each grade as a percentage of the selected project total.

SELECT
    quality_grade,
    COUNT(*) AS observation_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS project_percentage
FROM observations
WHERE project_alias = {{project_alias}}
GROUP BY quality_grade
ORDER BY observation_count DESC;
