DELETE FROM observations AS observation_rows
WHERE observation_rows.project_alias = %s
    AND observation_rows.observation_id = ANY(%s)
RETURNING observation_rows.observation_id;
