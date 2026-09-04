-- Counts research-grade species recorded per month and cumulatively for ABS, OBS, and their deduplicated aggregate.

WITH research_grade_species_observations AS (
    -- Convert every research-grade observation to its species-level taxon.
    SELECT
        observations.project_alias,
        observations.observation_id,
        DATE_TRUNC('month', observations.observed_on)::DATE AS period_start,
        COALESCE(species_taxa.taxon_id, CASE WHEN observed_taxa.rank = 'species' THEN observed_taxa.taxon_id END) AS species_taxon_id
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    LEFT JOIN LATERAL (
        SELECT lineage_taxa.taxon_id
        FROM jsonb_array_elements_text(
            COALESCE(observed_taxa.ancestor_ids, '[]'::JSONB)
        ) WITH ORDINALITY AS lineage_id(value, lineage_position)
        INNER JOIN taxa AS lineage_taxa
            ON lineage_taxa.taxon_id = lineage_id.value::BIGINT
        WHERE lineage_taxa.rank = 'species'
        ORDER BY lineage_id.lineage_position DESC
        LIMIT 1
    ) AS species_taxa ON TRUE
    WHERE observations.project_alias IN ('abs', 'obs')
        AND observations.quality_grade = 'research'
        AND observations.observed_on IS NOT NULL
),
species_observations AS (
    -- Keep ABS and OBS separately, then add one version of each observation for the aggregate.
    SELECT
        project_alias,
        period_start,
        species_taxon_id
    FROM research_grade_species_observations
    WHERE species_taxon_id IS NOT NULL
    UNION ALL
    SELECT
        project_alias,
        period_start,
        species_taxon_id
    FROM (
        SELECT DISTINCT ON (observation_id)
            'aggregated'::TEXT AS project_alias,
            period_start,
            species_taxon_id
        FROM research_grade_species_observations
        WHERE species_taxon_id IS NOT NULL
        ORDER BY
            observation_id,
            project_alias
    ) AS aggregated_observations
),
monthly_counts AS (
    -- Count species observed in each individual month.
    SELECT
        project_alias,
        period_start,
        COUNT(DISTINCT species_taxon_id) AS species_count
    FROM species_observations
    GROUP BY
        project_alias,
        period_start
),
calendar_months AS (
    -- Include quiet months so a cumulative line remains continuous.
    SELECT generated_month::DATE AS period_start
    FROM (
        SELECT
            MIN(period_start) AS first_period_start,
            MAX(period_start) AS last_period_start
        FROM species_observations
    ) AS bounds
    CROSS JOIN LATERAL generate_series(
        bounds.first_period_start,
        bounds.last_period_start,
        INTERVAL '1 month'
    ) AS generated_month
),
first_species_counts AS (
    -- A species contributes once: in the first month it was recorded.
    SELECT
        project_alias,
        first_period_start AS period_start,
        COUNT(*) AS first_species_count
    FROM (
        SELECT
            project_alias,
            species_taxon_id,
            MIN(period_start) AS first_period_start
        FROM species_observations
        GROUP BY
            project_alias,
            species_taxon_id
    ) AS first_species_months
    GROUP BY
        project_alias,
        first_period_start
)
SELECT
    aliases.project_alias,
    calendar_months.period_start,
    (calendar_months.period_start + INTERVAL '1 month - 1 day')::DATE AS period_end,
    COALESCE(monthly_counts.species_count, 0) AS species_count,
    SUM(COALESCE(first_species_counts.first_species_count, 0)) OVER (
        PARTITION BY aliases.project_alias
        ORDER BY calendar_months.period_start
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_species_count
FROM (
    VALUES
        ('abs'::TEXT),
        ('obs'::TEXT),
        ('aggregated'::TEXT)
) AS aliases(project_alias)
CROSS JOIN calendar_months
LEFT JOIN monthly_counts
    ON monthly_counts.project_alias = aliases.project_alias
    AND monthly_counts.period_start = calendar_months.period_start
LEFT JOIN first_species_counts
    ON first_species_counts.project_alias = aliases.project_alias
    AND first_species_counts.period_start = calendar_months.period_start
ORDER BY
    calendar_months.period_start,
    aliases.project_alias;
