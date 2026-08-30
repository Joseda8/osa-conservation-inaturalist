# Database schema

This diagram is derived from [`db/migrations/0001_initial_schema.sql`](../db/migrations/0001_initial_schema.sql). It shows the database entities, primary keys, and enforced foreign-key relationships. The migration remains the authoritative complete definition of every column and index.

```mermaid
erDiagram
    projects ||--o{ observations : contains
    taxa o|--o{ observations : identifies
    observers o|--o{ observations : submitted
    observations ||--o{ observation_photos : has

    projects {
        TEXT alias PK
        TEXT slug UK
        TEXT display_name
    }

    taxa {
        BIGINT taxon_id PK
        TEXT scientific_name
        TEXT common_name
        TEXT rank
        BIGINT parent_id
        JSONB ancestor_ids
        TEXT iconic_taxon_name
        BOOLEAN is_active
        TEXT loaded_from
        TIMESTAMPTZ loaded_at
    }

    observers {
        BIGINT observer_id PK
        TEXT login
        TEXT name
        INTEGER observations_count
        INTEGER species_count
        TEXT loaded_from
        TIMESTAMPTZ loaded_at
    }

    observations {
        TEXT project_alias PK, FK
        BIGINT observation_id PK
        DATE download_date
        TEXT quality_grade
        TIMESTAMPTZ observed_on
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
        BIGINT taxon_id FK
        BIGINT observer_id FK
        TEXT loaded_from
        TIMESTAMPTZ loaded_at
    }

    observation_photos {
        TEXT project_alias PK, FK
        BIGINT observation_id PK, FK
        BIGINT photo_id PK
        TEXT url
        TEXT license_code
        TEXT loaded_from
        TIMESTAMPTZ loaded_at
    }

    trends {
        TEXT region_key PK
        TEXT metric_name PK
        TEXT period_type PK
        DATE period_start PK
        TEXT dimension_type PK
        TEXT dimension_id PK
        DATE period_end
        NUMERIC value
        JSONB source_params
        TEXT loaded_from
        TIMESTAMPTZ loaded_at
    }
```

`taxa.parent_id` and `taxa.ancestor_ids` describe the taxonomic hierarchy, but the migration does not declare a foreign key for them. They are therefore intentionally not shown as an enforced relationship in the diagram.

`trends` stores independent aggregate metrics, so it has no foreign-key relationship to the other tables.
