-- Title: Observations by day by project
-- Description: Counts observations per observed day for each project. Bind observed_on to limit the date range.

SELECT
    project_alias,
    observed_on,
    COUNT(*) AS observations
FROM observations
WHERE observed_on IS NOT NULL
[[AND {{observed_on}}]]
GROUP BY
    project_alias,
    observed_on
ORDER BY
    project_alias,
    observed_on;
