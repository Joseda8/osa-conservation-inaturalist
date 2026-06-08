-- Title: Total participants by project
-- Description: Counts the number of distinct observers participating in each project.

SELECT
    project_alias,
    COUNT(DISTINCT observer_id) AS participants
FROM observations
WHERE observer_id IS NOT NULL
GROUP BY project_alias
ORDER BY
    participants DESC,
    project_alias;
