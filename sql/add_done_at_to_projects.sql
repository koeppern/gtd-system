-- Complete migration: Replace boolean done_status with timestamp done_at
-- This script performs the full migration and removes the old column

-- 1. Add done_at column if it doesn't exist
ALTER TABLE gtd_projects ADD COLUMN IF NOT EXISTS done_at TIMESTAMP WITH TIME ZONE;

-- 2. Update existing records: Set done_at = '1970-01-01' for projects where done_status = true
UPDATE gtd_projects 
SET done_at = '1970-01-01 00:00:00+00'::timestamptz
WHERE done_status = true AND done_at IS NULL;

-- 3. Verify the migration BEFORE removing done_status
SELECT 
    COUNT(*) as total_projects,
    COUNT(CASE WHEN done_at IS NOT NULL THEN 1 END) as completed_projects,
    COUNT(CASE WHEN done_at IS NULL THEN 1 END) as active_projects,
    COUNT(CASE WHEN done_status = true THEN 1 END) as old_completed,
    COUNT(CASE WHEN done_status = false THEN 1 END) as old_active
FROM gtd_projects 
WHERE deleted_at IS NULL;

-- 4. Check for consistency - should be zero inconsistencies
SELECT COUNT(*) as inconsistent_projects
FROM gtd_projects 
WHERE deleted_at IS NULL 
  AND ((done_status = true AND done_at IS NULL) OR (done_status = false AND done_at IS NOT NULL));

-- 5. Remove the old done_status column
ALTER TABLE gtd_projects DROP COLUMN IF EXISTS done_status;

-- 6. Final verification
SELECT 
    COUNT(*) as total_projects,
    COUNT(CASE WHEN done_at IS NOT NULL THEN 1 END) as completed_projects,
    COUNT(CASE WHEN done_at IS NULL THEN 1 END) as active_projects
FROM gtd_projects 
WHERE deleted_at IS NULL;