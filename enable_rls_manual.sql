-- Script to re-enable RLS on GTD tables after testing
-- Execute these commands in Supabase Dashboard -> SQL Editor

-- Re-enable RLS on gtd_projects table
ALTER TABLE gtd_projects ENABLE ROW LEVEL SECURITY;

-- Re-enable RLS on gtd_tasks table  
ALTER TABLE gtd_tasks ENABLE ROW LEVEL SECURITY;

-- Re-enable RLS on gtd_fields table
ALTER TABLE gtd_fields ENABLE ROW LEVEL SECURITY;

-- Re-enable RLS on gtd_users table
ALTER TABLE gtd_users ENABLE ROW LEVEL SECURITY;

-- Verify RLS status (optional check)
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('gtd_projects', 'gtd_tasks', 'gtd_fields', 'gtd_users')
ORDER BY tablename;