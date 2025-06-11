-- Create extensions for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create database if it doesn't exist (this script runs as superuser)
-- The database is already created by the POSTGRES_DB environment variable