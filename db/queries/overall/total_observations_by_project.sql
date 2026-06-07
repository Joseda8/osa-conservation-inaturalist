-- Title: Total observations by project
-- Description: Counts the total number of observations in each project.

SELECT
    project_alias,
    COUNT(*) AS observations
FROM observations
GROUP BY project_alias
ORDER BY
    observations DESC,
    project_alias;
