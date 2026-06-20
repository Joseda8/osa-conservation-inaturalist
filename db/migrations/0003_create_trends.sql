CREATE TABLE trends (
    region_key TEXT NOT NULL,
    region_type TEXT NOT NULL,
    region_label TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    period_type TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    dimension_type TEXT NOT NULL DEFAULT 'none',
    dimension_id TEXT NOT NULL DEFAULT 'none',
    dimension_label TEXT NOT NULL DEFAULT 'none',
    value NUMERIC NOT NULL,
    source_endpoint TEXT NOT NULL,
    source_params JSONB NOT NULL,
    raw_json JSONB NOT NULL,
    downloaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (
        region_key,
        metric_name,
        period_type,
        period_start,
        dimension_type,
        dimension_id
    )
);

CREATE INDEX idx_trends_metric_period
    ON trends(metric_name, period_type, period_start, period_end);

CREATE INDEX idx_trends_region_period
    ON trends(region_key, period_type, period_start, period_end);

CREATE INDEX idx_trends_dimension
    ON trends(dimension_type, dimension_id);
