-- Counts active observers and their average observation lifespan for ABS, OBS, and their deduplicated aggregate.

WITH project_observations AS (
    SELECT
        project_alias,
        observation_id,
        observer_id,
        created_at,
        observed_on
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
        AND observer_id IS NOT NULL
),
all_project_observations AS (
    SELECT
        project_alias,
        observer_id,
        created_at,
        observed_on
    FROM project_observations
    UNION ALL
    SELECT
        project_alias,
        observer_id,
        created_at,
        observed_on
    FROM (
        SELECT DISTINCT ON (observation_id)
            'aggregated'::TEXT AS project_alias,
            observer_id,
            created_at,
            observed_on
        FROM project_observations
        ORDER BY
            observation_id,
            project_alias
    ) AS aggregated_observations
),
active_observers AS (
    SELECT
        project_alias,
        observer_id,
        MIN(observed_on) AS first_observed_on,
        MAX(observed_on) AS last_observed_on
    FROM all_project_observations
    GROUP BY
        project_alias,
        observer_id
    HAVING BOOL_OR(created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year')
),
active_project_metrics AS (
    SELECT
        project_alias,
        COUNT(*) AS active_observer_count,
        ROUND(AVG(EXTRACT(EPOCH FROM last_observed_on - first_observed_on) / 86400), 1) AS average_observer_lifespan_days
    FROM active_observers
    GROUP BY project_alias
)
SELECT
    aliases.project_alias,
    'active_observers'::TEXT AS metric_id,
    COALESCE(active_project_metrics.active_observer_count, 0) AS active_observer_count,
    COALESCE(active_project_metrics.average_observer_lifespan_days, 0) AS average_observer_lifespan_days
FROM (
    VALUES
        ('abs'::TEXT),
        ('obs'::TEXT),
        ('aggregated'::TEXT)
) AS aliases(project_alias)
LEFT JOIN active_project_metrics
    ON active_project_metrics.project_alias = aliases.project_alias
ORDER BY aliases.project_alias;
