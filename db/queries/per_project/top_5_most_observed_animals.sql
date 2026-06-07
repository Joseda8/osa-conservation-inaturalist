-- Title: Top 5 most observed animals
-- Description: Shows the five most observed animal groups in one selected project, including each group's percentage of the project animal total.

SELECT
    project_rank,
    iconic_taxon_name,
    observation_count,
    project_total_observations,
    project_percentage
FROM (
    SELECT
        taxa.iconic_taxon_name,
        COUNT(*) AS observation_count,
        SUM(COUNT(*)) OVER () AS project_total_observations,
        ROUND(
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
            2
        ) AS project_percentage,
        ROW_NUMBER() OVER (
            ORDER BY COUNT(*) DESC, taxa.iconic_taxon_name
        ) AS project_rank
    FROM observations
    INNER JOIN taxa
        ON observations.taxon_id = taxa.taxon_id
    WHERE
        observations.project_alias = {{project_alias}}
        AND taxa.iconic_taxon_name IN (
            'Animalia',
            'Amphibia',
            'Arachnida',
            'Aves',
            'Actinopterygii',
            'Insecta',
            'Mammalia',
            'Mollusca',
            'Reptilia'
        )
    GROUP BY taxa.iconic_taxon_name
) AS ranked_animals
WHERE project_rank <= 5
ORDER BY project_rank;
