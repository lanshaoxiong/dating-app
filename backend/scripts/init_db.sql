-- Initialize PupMatch database with PostGIS extension
-- This script should be run by a PostgreSQL superuser

-- Create database if it doesn't exist
-- Note: This must be run outside a transaction block
-- Run with: psql -U postgres -f scripts/init_db.sql

-- Connect to the database
\c pupmatch

-- Enable PostGIS extension for geospatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify PostGIS installation
SELECT PostGIS_Version();

-- Create indexes will be handled by Alembic migrations
