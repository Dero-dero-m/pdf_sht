-- Runs once when the data directory is empty (i.e. on initial container setup).
-- The postgres entrypoint executes any *.sql / *.sh in /docker-entrypoint-initdb.d/
-- against the database named by POSTGRES_DB.

CREATE EXTENSION IF NOT EXISTS vector;
