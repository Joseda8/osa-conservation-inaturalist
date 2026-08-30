-- Counts observations by quality grade for each OSA project and both combined.

WITH project_quality_grade_counts AS (
    SELECT
        project_alias,
        quality_grade,
        COUNT(*) AS observation_count
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
    GROUP BY
        project_alias,
        quality_grade
),
aggregated_quality_grade_counts AS (
    SELECT
        'aggregated'::TEXT AS project_alias,
        quality_grade,
        COUNT(DISTINCT observation_id) AS observation_count
    FROM observations
    WHERE project_alias IN ('abs', 'obs')
    GROUP BY quality_grade
),
quality_grade_counts AS (
    SELECT
        project_alias,
        quality_grade,
        observation_count
    FROM project_quality_grade_counts
    UNION ALL
    SELECT
        project_alias,
        quality_grade,
        observation_count
    FROM aggregated_quality_grade_counts
)
SELECT
    project_alias,
    quality_grade,
    observation_count,
    SUM(CASE WHEN project_alias = 'aggregated' THEN observation_count ELSE 0 END) OVER () AS total_observation_count,
    SUM(observation_count) OVER (PARTITION BY project_alias) AS project_total_observation_count,
    ROUND(100.0 * observation_count / NULLIF(SUM(observation_count) OVER (PARTITION BY project_alias), 0), 1) AS project_observation_percentage
FROM quality_grade_counts
ORDER BY
    project_alias,
    quality_grade;
