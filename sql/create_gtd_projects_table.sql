-- Create GTD Projects table in Supabase
-- Run this in the Supabase SQL Editor

CREATE TABLE IF NOT EXISTS gtd_projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    notion_export_row INTEGER,
    done_status BOOLEAN,
    readings TEXT,
    field VARCHAR(50),
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

-- Create index for user_id for performance
CREATE INDEX IF NOT EXISTS idx_gtd_projects_user_id ON gtd_projects(user_id);