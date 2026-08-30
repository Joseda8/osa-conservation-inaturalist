-- Counts new observers by their first uploaded observation and the resulting cumulative observer total for ABS, OBS, and their deduplicated aggregate.

WITH project_observations AS (
    SELECT
        project_alias,
        observation_id,
        observer_id,
        created_at
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
        AND observer_id IS NOT NULL
        AND created_at IS NOT NULL
),
all_project_observations AS (
    SELECT
        project_alias,
        observer_id,
        created_at
    FROM project_observations
    UNION ALL
    SELECT
        project_alias,
        observer_id,
        created_at
    FROM (
        SELECT DISTINCT ON (observation_id)
            'aggregated'::TEXT AS project_alias,
            observer_id,
            created_at
        FROM project_observations
        ORDER BY
            observation_id,
            project_alias
    ) AS aggregated_observations
),
first_observer_uploads AS (
    SELECT
        project_alias,
        observer_id,
        DATE_TRUNC('month', MIN(created_at) AT TIME ZONE 'America/Costa_Rica')::DATE AS first_upload_month
    FROM all_project_observations
    GROUP BY
        project_alias,
        observer_id
),
monthly_new_observer_counts AS (
    SELECT
        project_alias,
        first_upload_month AS period_start,
        COUNT(*) AS new_observer_count
    FROM first_observer_uploads
    GROUP BY
        project_alias,
        first_upload_month
),
calendar_months AS (
    SELECT generated_month::DATE AS period_start
    FROM (
        SELECT
            MIN(period_start) AS first_period_start,
            MAX(period_start) AS last_period_start
        FROM monthly_new_observer_counts
    ) AS bounds
    CROSS JOIN LATERAL generate_series(
        bounds.first_period_start,
        bounds.last_period_start,
        INTERVAL '1 month'
    ) AS generated_month
)
SELECT
    aliases.project_alias,
    calendar_months.period_start,
    (calendar_months.period_start + INTERVAL '1 month - 1 day')::DATE AS period_end,
    COALESCE(monthly_new_observer_counts.new_observer_count, 0) AS new_observer_count,
    SUM(COALESCE(monthly_new_observer_counts.new_observer_count, 0)) OVER (
        PARTITION BY aliases.project_alias
        ORDER BY calendar_months.period_start
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_observer_count
FROM (
    VALUES
        ('abs'::TEXT),
        ('obs'::TEXT),
        ('aggregated'::TEXT)
) AS aliases(project_alias)
CROSS JOIN calendar_months
LEFT JOIN monthly_new_observer_counts
    ON monthly_new_observer_counts.project_alias = aliases.project_alias
    AND monthly_new_observer_counts.period_start = calendar_months.period_start
ORDER BY
    calendar_months.period_start,
    aliases.project_alias;
