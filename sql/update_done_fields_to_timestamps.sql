-- Update GTD schema to use done_at TIMESTAMP instead of BOOLEAN done fields
-- Run this AFTER creating the existing tables

-- =========================================
-- 1. Update GTD_PROJECTS table
-- =========================================

-- Add new done_at column
ALTER TABLE gtd_projects 
ADD COLUMN done_at TIMESTAMP NULL;

-- Migrate existing done_status data to done_at
-- If done_status is TRUE, set done_at to created_at (or current time if created_at is null)
UPDATE gtd_projects 
SET done_at = COALESCE(created_at, NOW()) 
WHERE done_status = true;

-- Drop the old boolean columns
ALTER TABLE gtd_projects 
DROP COLUMN IF EXISTS done_status,
DROP COLUMN IF EXISTS done_duplicate;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_gtd_projects_done_at ON gtd_projects(done_at);

-- =========================================
-- 2. Update GTD_TASKS table (if already created)
-- =========================================

-- Add new done_at column
ALTER TABLE gtd_tasks 
ADD COLUMN done_at TIMESTAMP NULL;

-- Migrate existing is_done data to done_at
-- If is_done is TRUE, set done_at to last_edited (or date_of_creation, or created_at)
UPDATE gtd_tasks 
SET done_at = COALESCE(last_edited, date_of_creation, created_at, NOW()) 
WHERE is_done = true;

-- Drop the old boolean column
ALTER TABLE gtd_tasks 
DROP COLUMN IF EXISTS is_done;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_done_at ON gtd_tasks(done_at);

-- =========================================
-- 3. Update VIEWS to use done_at
-- =========================================

-- Drop existing views
DROP VIEW IF EXISTS gtd_projects_with_fields;
DROP VIEW IF EXISTS gtd_tasks_with_details;
DROP VIEW IF EXISTS gtd_tasks_summary;

-- Recreate projects view with done_at
CREATE OR REPLACE VIEW gtd_projects_with_fields AS
SELECT 
    p.*,
    f.name as field_name,
    f.description as field_description,
    CASE WHEN p.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id;

-- Recreate tasks detail view with done_at
CREATE OR REPLACE VIEW gtd_tasks_with_details AS
SELECT 
    t.*,
    p.project_name,
    p.readings as project_readings,
    f.name as field_name,
    f.description as field_description,
    CASE WHEN t.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_tasks t
LEFT JOIN gtd_projects p ON t.project_id = p.id
LEFT JOIN gtd_fields f ON t.field_id = f.id;

-- Recreate tasks summary view with done_at
CREATE OR REPLACE VIEW gtd_tasks_summary AS
SELECT 
    user_id,
    COUNT(*) as total_tasks,
    COUNT(CASE WHEN done_at IS NOT NULL THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN done_at IS NULL THEN 1 END) as pending_tasks,
    COUNT(CASE WHEN do_today = true AND done_at IS NULL THEN 1 END) as tasks_for_today,
    COUNT(CASE WHEN do_this_week = true AND done_at IS NULL THEN 1 END) as tasks_this_week,
    COUNT(CASE WHEN wait_for = true AND done_at IS NULL THEN 1 END) as waiting_tasks,
    COUNT(CASE WHEN postponed = true AND done_at IS NULL THEN 1 END) as postponed_tasks,
    -- Additional analytics with done_at
    COUNT(CASE WHEN done_at >= CURRENT_DATE THEN 1 END) as completed_today,
    COUNT(CASE WHEN done_at >= DATE_TRUNC('week', CURRENT_DATE) THEN 1 END) as completed_this_week,
    COUNT(CASE WHEN done_at >= DATE_TRUNC('month', CURRENT_DATE) THEN 1 END) as completed_this_month
FROM gtd_tasks
WHERE deleted_at IS NULL
GROUP BY user_id;

-- =========================================
-- 4. Create analytics views for completion tracking
-- =========================================

-- Daily completion statistics
CREATE OR REPLACE VIEW gtd_completion_daily AS
SELECT 
    user_id,
    DATE(done_at) as completion_date,
    COUNT(*) as tasks_completed,
    COUNT(DISTINCT project_id) as projects_touched
FROM gtd_tasks
WHERE done_at IS NOT NULL
    AND deleted_at IS NULL
GROUP BY user_id, DATE(done_at)
ORDER BY completion_date DESC;

-- Weekly completion statistics  
CREATE OR REPLACE VIEW gtd_completion_weekly AS
SELECT 
    user_id,
    DATE_TRUNC('week', done_at) as week_start,
    COUNT(*) as tasks_completed,
    COUNT(DISTINCT project_id) as projects_touched,
    AVG(EXTRACT(epoch FROM (done_at - date_of_creation))/86400)::DECIMAL(10,2) as avg_days_to_complete
FROM gtd_tasks
WHERE done_at IS NOT NULL
    AND deleted_at IS NULL
    AND date_of_creation IS NOT NULL
GROUP BY user_id, DATE_TRUNC('week', done_at)
ORDER BY week_start DESC;

-- Project completion analytics
CREATE OR REPLACE VIEW gtd_project_completion_stats AS
SELECT 
    p.user_id,
    p.id as project_id,
    p.project_name,
    p.done_at as project_done_at,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.done_at IS NOT NULL THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.done_at IS NULL THEN 1 END) as pending_tasks,
    CASE 
        WHEN COUNT(t.id) = 0 THEN 0
        ELSE ROUND((COUNT(CASE WHEN t.done_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(t.id)), 2)
    END as completion_percentage,
    MIN(t.date_of_creation) as first_task_created,
    MAX(t.done_at) as last_task_completed
FROM gtd_projects p
LEFT JOIN gtd_tasks t ON p.id = t.project_id AND t.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.user_id, p.id, p.project_name, p.done_at
ORDER BY completion_percentage DESC, p.project_name;