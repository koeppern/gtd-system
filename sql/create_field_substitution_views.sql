-- =========================================
-- CREATE FIELD SUBSTITUTION VIEWS
-- =========================================
-- This script creates views that substitute field_ids with field_names

-- Drop existing views if they exist
DROP VIEW IF EXISTS gtd_tasks_with_field_names CASCADE;
DROP VIEW IF EXISTS gtd_projects_with_field_names CASCADE;

-- Create view for tasks with field names instead of field_ids
CREATE VIEW gtd_tasks_with_field_names AS
SELECT 
    t.*,
    f.field_name
FROM gtd_tasks t
LEFT JOIN gtd_fields f ON t.field_id = f.id;

-- Create view for projects with field names instead of field_ids  
CREATE VIEW gtd_projects_with_field_names AS
SELECT 
    p.*,
    f.field_name
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id;

-- Create enhanced task view with project name and field name
CREATE VIEW gtd_tasks_enhanced AS
SELECT 
    t.*,
    f.field_name,
    p.project_name
FROM gtd_tasks t
LEFT JOIN gtd_fields f ON t.field_id = f.id
LEFT JOIN gtd_projects p ON t.project_id = p.id;

-- Create enhanced project view with field name and task count
CREATE VIEW gtd_projects_enhanced AS
SELECT 
    p.*,
    f.field_name,
    COALESCE(task_counts.task_count, 0) as task_count
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id
LEFT JOIN (
    SELECT 
        project_id,
        COUNT(*) as task_count
    FROM gtd_tasks 
    WHERE deleted_at IS NULL
    GROUP BY project_id
) task_counts ON p.id = task_counts.project_id;

-- Grant permissions
GRANT SELECT ON gtd_tasks_with_field_names TO postgres;
GRANT SELECT ON gtd_projects_with_field_names TO postgres;
GRANT SELECT ON gtd_tasks_enhanced TO postgres;
GRANT SELECT ON gtd_projects_enhanced TO postgres;

-- Print confirmation
DO $$
BEGIN
    RAISE NOTICE 'Field substitution views created successfully!';
    RAISE NOTICE 'Views: gtd_tasks_with_field_names, gtd_projects_with_field_names';
    RAISE NOTICE 'Enhanced views: gtd_tasks_enhanced, gtd_projects_enhanced';
    RAISE NOTICE 'These views automatically substitute field_id with field_name';
END $$;