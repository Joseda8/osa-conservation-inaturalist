-- Title: Observations by year
-- Description: Counts observations per observed year for one selected project.

SELECT
    EXTRACT(YEAR FROM observed_on)::INTEGER AS observed_year,
    COUNT(*) AS observations
FROM observations
WHERE
    project_alias = {{project_alias}}
    AND observed_on IS NOT NULL
GROUP BY EXTRACT(YEAR FROM observed_on)
ORDER BY EXTRACT(YEAR FROM observed_on);
