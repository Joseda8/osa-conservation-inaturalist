-- Title: Observations by year by project
-- Description: Counts observations per observed year for each project.

SELECT
    project_alias,
    EXTRACT(YEAR FROM observed_on)::INTEGER AS observed_year,
    COUNT(*) AS observations
FROM observations
WHERE observed_on IS NOT NULL
GROUP BY
    project_alias,
    EXTRACT(YEAR FROM observed_on)
ORDER BY
    project_alias,
    EXTRACT(YEAR FROM observed_on);
