DELETE FROM observers AS observer_rows
WHERE NOT EXISTS (
    SELECT 1
    FROM observations AS observation_rows
    WHERE observation_rows.observer_id = observer_rows.observer_id
);
