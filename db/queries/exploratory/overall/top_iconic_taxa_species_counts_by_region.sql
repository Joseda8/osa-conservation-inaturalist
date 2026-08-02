-- Title: Top iconic taxa species counts by region
-- Description: Shows the top iconic taxa by summed monthly species count for a selected observed-date timespan. Bind period_start to trends.period_start and region_key to trends.region_key; top_n is optional.

WITH iconic_taxa_counts AS (
    SELECT
        region_key,
        region_label,
        dimension_id AS taxon_id,
        dimension_label AS iconic_taxon,
        SUM(value) AS species_count
    FROM trends
    WHERE metric_name = 'iconic_taxon_species_count'
        AND period_type = 'month'
        AND dimension_type = 'iconic_taxon'
        [[AND {{period_start}}]]
        [[AND {{region_key}}]]
    GROUP BY
        region_key,
        region_label,
        dimension_id,
        dimension_label
),
ranked_iconic_taxa AS (
    SELECT
        region_key,
        region_label,
        taxon_id,
        iconic_taxon,
        species_count,
        ROW_NUMBER() OVER (
            PARTITION BY region_key
            ORDER BY species_count DESC, iconic_taxon
        ) AS taxon_rank
    FROM iconic_taxa_counts
)
SELECT
    region_key,
    region_label,
    taxon_id,
    iconic_taxon,
    species_count
FROM ranked_iconic_taxa
WHERE taxon_rank <= [[{{top_n}} --]] 5
ORDER BY
    taxon_rank,
	region_key;
