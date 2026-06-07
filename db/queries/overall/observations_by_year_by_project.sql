-- Title: Observations by year by project
-- Description: Counts observations per observed year for each project.

SELECT
    project_alias,
    observed_year,
    COUNT(*) AS observations
FROM observations
WHERE observed_year IS NOT NULL
GROUP BY
    project_alias,
    observed_year
ORDER BY
    project_alias,
    observed_year;
