-- copilot_roles.sql
-- Run manually on any new PostgreSQL server
-- Replace 'your_db_name' with actual DB name

CREATE USER copilot_reader WITH PASSWORD 'ghanimcopilot@1029';
GRANT CONNECT ON DATABASE your_db_name TO copilot_reader;
GRANT USAGE ON SCHEMA public TO copilot_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO copilot_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO copilot_reader;