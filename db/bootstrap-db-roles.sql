-- Bootstrap separate PostgreSQL identities for OpenCyberRange.
--
-- Run as the database superuser (the POSTGRES_USER created by the official
-- image) through scripts/bootstrap-db-roles.sh. The file is idempotent.
--
-- Roles:
--   ocr_migrator   owns schema objects; runs Alembic and startup DDL
--   ocr_runtime    request traffic; NOBYPASSRLS so tenant RLS is enforced
--   ocr_reporting  read-only cross-tenant reporting
--   ocr_backup     pg_dump / restore verification
--   ocr_audit      read-only security, consent, and change-ledger access
--
-- Passwords are supplied by environment variables and read with \getenv so
-- they never appear in the SQL file or shell history.

\set ON_ERROR_STOP on
\getenv migrator_password OCR_DB_MIGRATOR_PASSWORD
\getenv runtime_password OCR_DB_RUNTIME_PASSWORD
\getenv reporting_password OCR_DB_REPORTING_PASSWORD
\getenv backup_password OCR_DB_BACKUP_PASSWORD
\getenv audit_password OCR_DB_AUDIT_PASSWORD

SELECT length(:'migrator_password') >= 32 AS ok \gset
\if :ok
\else
  \echo 'OCR_DB_MIGRATOR_PASSWORD must be at least 32 characters'
  \quit 1
\endif
SELECT length(:'runtime_password') >= 32 AS ok \gset
\if :ok
\else
  \echo 'OCR_DB_RUNTIME_PASSWORD must be at least 32 characters'
  \quit 1
\endif
SELECT length(:'reporting_password') >= 32 AS ok \gset
\if :ok
\else
  \echo 'OCR_DB_REPORTING_PASSWORD must be at least 32 characters'
  \quit 1
\endif
SELECT length(:'backup_password') >= 32 AS ok \gset
\if :ok
\else
  \echo 'OCR_DB_BACKUP_PASSWORD must be at least 32 characters'
  \quit 1
\endif
SELECT length(:'audit_password') >= 32 AS ok \gset
\if :ok
\else
  \echo 'OCR_DB_AUDIT_PASSWORD must be at least 32 characters'
  \quit 1
\endif

SELECT current_database() AS dbname \gset

DO $$
DECLARE role_name text;
BEGIN
  FOREACH role_name IN ARRAY ARRAY[
    'ocr_migrator', 'ocr_runtime', 'ocr_reporting', 'ocr_backup', 'ocr_audit'
  ] LOOP
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
      EXECUTE format('CREATE ROLE %I LOGIN', role_name);
    END IF;
  END LOOP;
END $$;

ALTER ROLE ocr_migrator WITH LOGIN PASSWORD :'migrator_password'  -- security-delta: allow credential-like assignment
  NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT BYPASSRLS;
ALTER ROLE ocr_runtime WITH LOGIN PASSWORD :'runtime_password'  -- security-delta: allow credential-like assignment
  NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOBYPASSRLS;
ALTER ROLE ocr_reporting WITH LOGIN PASSWORD :'reporting_password'  -- security-delta: allow credential-like assignment
  NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT BYPASSRLS;
ALTER ROLE ocr_backup WITH LOGIN PASSWORD :'backup_password'  -- security-delta: allow credential-like assignment
  NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT BYPASSRLS;
ALTER ROLE ocr_audit WITH LOGIN PASSWORD :'audit_password'  -- security-delta: allow credential-like assignment
  NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT BYPASSRLS;

GRANT CONNECT ON DATABASE :"dbname"
  TO ocr_migrator, ocr_runtime, ocr_reporting, ocr_backup, ocr_audit;
GRANT USAGE ON SCHEMA public
  TO ocr_migrator, ocr_runtime, ocr_reporting, ocr_backup, ocr_audit;
GRANT CREATE ON SCHEMA public TO ocr_migrator;

-- Move existing objects to the migrator identity. A table owner bypasses RLS
-- unless FORCE ROW LEVEL SECURITY is set; the migrator has BYPASSRLS so data
-- backfills can see every tenant, while the runtime role does not.
DO $$
DECLARE obj record;
BEGIN
  FOR obj IN
    SELECT c.oid::regclass AS name, c.relkind
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
      -- A sequence owned by a table follows the table owner; ALTER SEQUENCE
      -- on it fails with "linked to table". The table branch handles it.
      AND NOT (
        c.relkind = 'S'
        AND EXISTS (
          SELECT 1 FROM pg_depend d
          WHERE d.objid = c.oid AND d.deptype IN ('a', 'i')
        )
      )
  LOOP
    IF obj.relkind = 'S' THEN
      EXECUTE format('ALTER SEQUENCE %s OWNER TO ocr_migrator', obj.name);
    ELSIF obj.relkind = 'v' THEN
      EXECUTE format('ALTER VIEW %s OWNER TO ocr_migrator', obj.name);
    ELSIF obj.relkind = 'm' THEN
      EXECUTE format('ALTER MATERIALIZED VIEW %s OWNER TO ocr_migrator', obj.name);
    ELSIF obj.relkind = 'f' THEN
      EXECUTE format('ALTER FOREIGN TABLE %s OWNER TO ocr_migrator', obj.name);
    ELSE
      EXECUTE format('ALTER TABLE %s OWNER TO ocr_migrator', obj.name);
    END IF;
  END LOOP;

  FOR obj IN
    SELECT p.oid::regprocedure AS name, p.prokind
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
  LOOP
    IF obj.prokind = 'a' THEN
      EXECUTE format('ALTER AGGREGATE %s OWNER TO ocr_migrator', obj.name);
    ELSIF obj.prokind = 'p' THEN
      EXECUTE format('ALTER PROCEDURE %s OWNER TO ocr_migrator', obj.name);
    ELSE
      EXECUTE format('ALTER FUNCTION %s OWNER TO ocr_migrator', obj.name);
    END IF;
  END LOOP;

  FOR obj IN
    SELECT t.oid::regtype AS name, t.typtype
    FROM pg_type t
    JOIN pg_namespace n ON n.oid = t.typnamespace
    WHERE n.nspname = 'public'
      AND t.typtype IN ('c', 'd', 'e', 'r')
      AND t.typrelid = 0
  LOOP
    IF obj.typtype = 'd' THEN
      EXECUTE format('ALTER DOMAIN %s OWNER TO ocr_migrator', obj.name);
    ELSE
      EXECUTE format('ALTER TYPE %s OWNER TO ocr_migrator', obj.name);
    END IF;
  END LOOP;
END $$;

-- Runtime DML. The runtime role must not own tables and must not bypass RLS.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ocr_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ocr_runtime;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ocr_runtime;

-- Reporting and backup need cross-tenant reads. pg_read_all_data covers
-- current and future tables; BYPASSRLS is required for pg_dump and cohort
-- reporting that intentionally spans institutions.
GRANT pg_read_all_data TO ocr_reporting, ocr_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ocr_reporting, ocr_backup;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO ocr_reporting, ocr_backup;

-- Audit identity: only the append-only evidence and security tables.
DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'security_events', 'activity_events', 'consent_audits', 'consent_events',
    'break_glass_grants', 'db_change_ledger'
  ] LOOP
    IF to_regclass('public.' || table_name) IS NOT NULL THEN
      EXECUTE format('GRANT SELECT ON public.%I TO ocr_audit', table_name);
    END IF;
  END LOOP;
END $$;

-- Enumerated and domain types need USAGE for inserts and casts.
DO $$
DECLARE obj record;
BEGIN
  FOR obj IN
    SELECT t.oid::regtype AS name
    FROM pg_type t
    JOIN pg_namespace n ON n.oid = t.typnamespace
    WHERE n.nspname = 'public'
      AND t.typtype IN ('e', 'd')
  LOOP
    EXECUTE format('GRANT USAGE ON TYPE %s TO ocr_runtime, ocr_reporting, ocr_backup, ocr_audit', obj.name);
  END LOOP;
END $$;

-- Future objects created by the migrator inherit the runtime/reporting grants.
ALTER DEFAULT PRIVILEGES FOR ROLE ocr_migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ocr_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE ocr_migrator IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO ocr_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE ocr_migrator IN SCHEMA public
  GRANT EXECUTE ON FUNCTIONS TO ocr_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE ocr_migrator IN SCHEMA public
  GRANT USAGE ON TYPES TO ocr_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE ocr_migrator IN SCHEMA public
  GRANT SELECT ON TABLES TO ocr_reporting, ocr_backup;

SELECT 'ocr roles ready: ' || string_agg(rolname, ', ' ORDER BY rolname)
FROM pg_roles
WHERE rolname LIKE 'ocr\_%' ESCAPE '\';
