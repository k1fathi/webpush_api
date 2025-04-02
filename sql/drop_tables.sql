DO $$
DECLARE r RECORD;
BEGIN -- Iterate over all tables in the current schema
FOR r IN (
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public'
) LOOP EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
END LOOP;
END $$;