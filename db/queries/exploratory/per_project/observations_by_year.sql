-- Title: Observations by year
-- Description: Counts observations per observed year for one selected project.

SELECT
    observed_year,
    COUNT(*) AS observations
FROM observations
WHERE
    project_alias = {{project_alias}}
    AND observed_year IS NOT NULL
GROUP BY observed_year
ORDER BY observed_year;
