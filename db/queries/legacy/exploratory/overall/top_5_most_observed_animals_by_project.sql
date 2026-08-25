-- Title: Top 5 most observed animals by project
-- Description: Shows the five most observed animal groups in each project, including each group's percentage of the project animal total.

SELECT
    project_alias,
    project_rank,
    iconic_taxon_name,
    observation_count,
    project_total_observations,
    project_percentage
FROM (
    SELECT
        observations.project_alias,
        taxa.iconic_taxon_name,
        COUNT(*) AS observation_count,
        SUM(COUNT(*)) OVER (
            PARTITION BY observations.project_alias
        ) AS project_total_observations,
        ROUND(
            COUNT(*) * 100.0
            / SUM(COUNT(*)) OVER (PARTITION BY observations.project_alias),
            2
        ) AS project_percentage,
        ROW_NUMBER() OVER (
            PARTITION BY observations.project_alias
            ORDER BY COUNT(*) DESC, taxa.iconic_taxon_name
        ) AS project_rank
    FROM observations
    INNER JOIN taxa
        ON observations.taxon_id = taxa.taxon_id
    WHERE taxa.iconic_taxon_name IN (
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
    GROUP BY
        observations.project_alias,
        taxa.iconic_taxon_name
) AS ranked_animals
WHERE project_rank <= 5
ORDER BY
    project_alias,
    project_rank;
