-- Normalized Schema for GTD Projects with separate FIELDS table
-- Run this in the Supabase SQL Editor

-- Step 1: Drop existing table if it exists
DROP TABLE IF EXISTS gtd_projects CASCADE;

-- Step 2: Create FIELDS lookup table
CREATE TABLE gtd_fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Step 3: Insert default field values
INSERT INTO gtd_fields (name, description) VALUES 
    ('Private', 'Personal projects and tasks'),
    ('Work', 'Professional projects and tasks');

-- Step 4: Create GTD Projects table with foreign key to FIELDS
CREATE TABLE gtd_projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    notion_export_row INTEGER,
    done_status BOOLEAN,
    readings TEXT,
    field_id INTEGER REFERENCES gtd_fields(id),
    keywords TEXT,
    done_duplicate BOOLEAN,
    mother_project TEXT,
    related_projects TEXT,
    related_mother_projects TEXT,
    related_knowledge_vault TEXT,
    related_tasks TEXT,
    do_this_week BOOLEAN,
    gtd_processes TEXT,
    add_checkboxes TEXT,
    project_name TEXT,
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Step 5: Create indexes for performance
CREATE INDEX idx_gtd_projects_user_id ON gtd_projects(user_id);
CREATE INDEX idx_gtd_projects_field_id ON gtd_projects(field_id);

-- Step 6: Create a view for easy querying with field names
CREATE VIEW gtd_projects_with_fields AS
SELECT 
    p.*,
    f.name as field_name,
    f.description as field_description
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id;

-- Step 7: Grant necessary permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON gtd_projects TO authenticated;
-- GRANT SELECT ON gtd_fields TO authenticated;
-- GRANT SELECT ON gtd_projects_with_fields TO authenticated;