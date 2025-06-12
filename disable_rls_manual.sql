-- Script to temporarily disable RLS on GTD tables for testing
-- Execute these commands in Supabase Dashboard -> SQL Editor

-- Disable RLS on gtd_projects table
ALTER TABLE gtd_projects DISABLE ROW LEVEL SECURITY;

-- Disable RLS on gtd_tasks table  
ALTER TABLE gtd_tasks DISABLE ROW LEVEL SECURITY;

-- Disable RLS on gtd_fields table
ALTER TABLE gtd_fields DISABLE ROW LEVEL SECURITY;

-- Disable RLS on gtd_users table
ALTER TABLE gtd_users DISABLE ROW LEVEL SECURITY;

-- Verify RLS status (optional check)
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('gtd_projects', 'gtd_tasks', 'gtd_fields', 'gtd_users')
ORDER BY tablename;