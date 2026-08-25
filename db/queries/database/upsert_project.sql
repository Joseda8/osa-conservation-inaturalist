INSERT INTO projects (alias, slug, display_name)
VALUES (%s, %s, %s)
ON CONFLICT (alias) DO UPDATE SET
    slug = EXCLUDED.slug,
    display_name = EXCLUDED.display_name;
