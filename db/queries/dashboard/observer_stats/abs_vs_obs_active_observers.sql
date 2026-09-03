-- Compares active and inactive observers and reports active-observer lifespan for ABS, OBS, and their deduplicated aggregate.

WITH project_observations AS (
    SELECT
        project_alias,
        observation_id,
        observer_id,
        created_at,
        COALESCE(observed_at, observed_on::TIMESTAMPTZ) AS observed_at
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
        AND observer_id IS NOT NULL
),
all_project_observations AS (
    SELECT
        project_alias,
        observer_id,
        created_at,
        observed_at
    FROM project_observations
    UNION ALL
    SELECT
        project_alias,
        observer_id,
        created_at,
        observed_at
    FROM (
        SELECT DISTINCT ON (observation_id)
            'aggregated'::TEXT AS project_alias,
            observer_id,
            created_at,
            observed_at
        FROM project_observations
        ORDER BY
            observation_id,
            project_alias
    ) AS aggregated_observations
),
observer_metrics AS (
    SELECT
        project_alias,
        observer_id,
        COALESCE(BOOL_OR(created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'), FALSE) AS is_active,
        MIN(observed_at) AS first_observed_at,
        MAX(observed_at) AS last_observed_at
    FROM all_project_observations
    GROUP BY
        project_alias,
        observer_id
),
project_metrics AS (
    SELECT
        project_alias,
        COUNT(*) AS total_observer_count,
        COUNT(*) FILTER (WHERE is_active) AS active_observer_count,
        COUNT(*) FILTER (WHERE NOT is_active) AS inactive_observer_count,
        ROUND(AVG(EXTRACT(EPOCH FROM last_observed_at - first_observed_at) / 86400) FILTER (WHERE is_active), 1) AS average_active_observer_lifespan_days
    FROM observer_metrics
    GROUP BY project_alias
)
SELECT
    aliases.project_alias,
    activity_status.activity_status,
    activity_status.observer_count,
    COALESCE(project_metrics.total_observer_count, 0) AS total_observer_count,
    ROUND(100.0 * activity_status.observer_count / NULLIF(project_metrics.total_observer_count, 0), 1) AS observer_percentage,
    COALESCE(project_metrics.average_active_observer_lifespan_days, 0) AS average_active_observer_lifespan_days
FROM (
    VALUES
        ('abs'::TEXT),
        ('obs'::TEXT),
        ('aggregated'::TEXT)
) AS aliases(project_alias)
LEFT JOIN project_metrics
    ON project_metrics.project_alias = aliases.project_alias
CROSS JOIN LATERAL (
    VALUES
        ('active'::TEXT, COALESCE(project_metrics.active_observer_count, 0)),
        ('inactive'::TEXT, COALESCE(project_metrics.inactive_observer_count, 0))
) AS activity_status(activity_status, observer_count)
ORDER BY
    activity_status.activity_status,
    aliases.project_alias;
