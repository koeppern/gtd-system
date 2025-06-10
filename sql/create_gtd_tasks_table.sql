-- Create GTD Tasks table with normalized structure
-- Run this in the Supabase SQL Editor after running create_normalized_schema.sql

-- Create GTD Tasks table
CREATE TABLE IF NOT EXISTS gtd_tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    notion_export_row INTEGER,
    
    -- Core task information
    task_name TEXT NOT NULL,
    project_id INTEGER REFERENCES gtd_projects(id) ON DELETE SET NULL,
    project_reference TEXT, -- Raw project reference from CSV for debugging
    
    -- Status flags (converted from Yes/No to boolean)
    done_at TIMESTAMP NULL, -- When task was completed (NULL = not done)
    do_today BOOLEAN DEFAULT FALSE,
    do_this_week BOOLEAN DEFAULT FALSE,
    is_reading BOOLEAN DEFAULT FALSE,
    wait_for BOOLEAN DEFAULT FALSE,
    postponed BOOLEAN DEFAULT FALSE,
    reviewed BOOLEAN DEFAULT FALSE,
    
    -- Dates and timing
    do_on_date DATE,
    last_edited TIMESTAMP,
    date_of_creation TIMESTAMP,
    
    -- Additional fields
    field_id INTEGER REFERENCES gtd_fields(id) ON DELETE SET NULL,
    priority INTEGER,
    time_expenditure TEXT,
    url TEXT,
    knowledge_db_entry TEXT,
    
    -- Metadata
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_user_id ON gtd_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_project_id ON gtd_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_field_id ON gtd_tasks(field_id);
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_done_at ON gtd_tasks(done_at);
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_do_today ON gtd_tasks(do_today);
CREATE INDEX IF NOT EXISTS idx_gtd_tasks_do_this_week ON gtd_tasks(do_this_week);

-- Create view for easy querying with field and project names
CREATE OR REPLACE VIEW gtd_tasks_with_details AS
SELECT 
    t.*,
    p.project_name,
    p.readings as project_readings,
    f.name as field_name,
    f.description as field_description
FROM gtd_tasks t
LEFT JOIN gtd_projects p ON t.project_id = p.id
LEFT JOIN gtd_fields f ON t.field_id = f.id;

-- Add trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_gtd_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_gtd_tasks_updated_at
    BEFORE UPDATE ON gtd_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_gtd_tasks_updated_at();

-- Create summary statistics view with done_at
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

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON gtd_tasks TO authenticated;
-- GRANT SELECT ON gtd_tasks_with_details TO authenticated;
-- GRANT SELECT ON gtd_tasks_summary TO authenticated;