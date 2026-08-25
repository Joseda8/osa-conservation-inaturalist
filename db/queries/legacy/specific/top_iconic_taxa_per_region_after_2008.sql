-- Title: Top iconic taxa per region after 2008
-- Description: Shows the top iconic taxa by summed monthly species count for each region after 2008. Change top_n to adjust the number of rows per region.

WITH query_parameters AS (
    SELECT 5 AS top_n
),
iconic_taxa_counts AS (
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
        AND period_start >= DATE '2009-01-01'
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
	taxon_rank,
    region_label,
    iconic_taxon,
    species_count
FROM ranked_iconic_taxa
WHERE taxon_rank <= (SELECT top_n FROM query_parameters)
ORDER BY
    taxon_rank,
    CASE region_key
        WHEN 'costa_rica' THEN 1
        WHEN 'abs' THEN 2
        WHEN 'obs' THEN 3
        ELSE 4
    END,
    iconic_taxon;
