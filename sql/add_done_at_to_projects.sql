-- Add done_at column to gtd_projects table and migrate existing done_status data
-- Migration: Replace boolean done_status with timestamp done_at

-- 1. Add done_at column if it doesn't exist
ALTER TABLE gtd_projects ADD COLUMN IF NOT EXISTS done_at TIMESTAMP WITH TIME ZONE;

-- 2. Update existing records: Set done_at = '1970-01-01' for projects where done_status = true
UPDATE gtd_projects 
SET done_at = '1970-01-01 00:00:00+00'::timestamptz
WHERE done_status = true AND done_at IS NULL;

-- 3. Verify the migration
SELECT 
    COUNT(*) as total_projects,
    COUNT(CASE WHEN done_at IS NOT NULL THEN 1 END) as completed_projects,
    COUNT(CASE WHEN done_at IS NULL THEN 1 END) as active_projects
FROM gtd_projects 
WHERE deleted_at IS NULL;

-- 4. Show examples of migrated data
SELECT 
    project_name,
    done_status,
    done_at,
    CASE 
        WHEN done_at IS NOT NULL THEN 'COMPLETED' 
        ELSE 'ACTIVE' 
    END as new_status
FROM gtd_projects 
WHERE deleted_at IS NULL
ORDER BY done_at DESC NULLS LAST
LIMIT 10;