-- Title: Average participant lifetime by project
-- Description: Calculates the average span between each participant's first and last observation date in each project.

WITH participant_lifetimes AS (
    SELECT
        project_alias,
        observer_id,
        MIN(observed_on) AS first_observed_on,
        MAX(observed_on) AS last_observed_on,
        MAX(observed_on) - MIN(observed_on) AS lifetime_days
    FROM observations
    WHERE observer_id IS NOT NULL
        AND observed_on IS NOT NULL
    GROUP BY
        project_alias,
        observer_id
)
SELECT
    project_alias,
    COUNT(*) AS participants,
    ROUND(AVG(lifetime_days), 2) AS average_lifetime_days
FROM participant_lifetimes
GROUP BY project_alias
ORDER BY
    average_lifetime_days DESC,
    project_alias;
