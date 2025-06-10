-- =========================================
-- COMPLETE GTD DATABASE SETUP - CONSOLIDATION
-- =========================================
-- This script will clean up existing tables and create a clean schema

-- Step 1: Drop all existing GTD tables to start fresh
DROP TABLE IF EXISTS gtd_tasks CASCADE;
DROP TABLE IF EXISTS gtd_projects CASCADE;
DROP TABLE IF EXISTS gtd_users CASCADE;
DROP TABLE IF EXISTS gtd_fields CASCADE;

-- Drop any views that might exist
DROP VIEW IF EXISTS gtd_projects_with_fields CASCADE;
DROP VIEW IF EXISTS gtd_tasks_with_details CASCADE;
DROP VIEW IF EXISTS gtd_projects_with_user_details CASCADE;
DROP VIEW IF EXISTS gtd_tasks_with_user_details CASCADE;
DROP VIEW IF EXISTS gtd_user_dashboard CASCADE;
DROP VIEW IF EXISTS gtd_tasks_summary CASCADE;
DROP VIEW IF EXISTS gtd_completion_daily CASCADE;
DROP VIEW IF EXISTS gtd_completion_weekly CASCADE;
DROP VIEW IF EXISTS gtd_project_completion_stats CASCADE;

-- Drop any functions/triggers
DROP TRIGGER IF EXISTS trigger_gtd_users_updated_at ON gtd_users;
DROP TRIGGER IF EXISTS trigger_gtd_projects_updated_at ON gtd_projects;
DROP TRIGGER IF EXISTS trigger_gtd_tasks_updated_at ON gtd_tasks;
DROP FUNCTION IF EXISTS update_gtd_users_updated_at();
DROP FUNCTION IF EXISTS update_gtd_projects_updated_at();
DROP FUNCTION IF EXISTS update_gtd_tasks_updated_at();

-- =========================================
-- Step 2: Create GTD Users table FIRST
-- =========================================
CREATE TABLE gtd_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic user information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email_address VARCHAR(255) UNIQUE NOT NULL,
    
    -- User preferences
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    date_format VARCHAR(20) DEFAULT 'DD.MM.YYYY',
    time_format VARCHAR(10) DEFAULT '24h',
    
    -- GTD-specific settings
    weekly_review_day INTEGER DEFAULT 0, -- 0=Sunday, 1=Monday, etc.
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- =========================================
-- Step 3: Create GTD Fields lookup table
-- =========================================
CREATE TABLE gtd_fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default field values
INSERT INTO gtd_fields (name, description) VALUES 
    ('Private', 'Persönliche Projekte und Aufgaben'),
    ('Work', 'Berufliche Projekte und Aufgaben');

-- =========================================
-- Step 4: Create GTD Projects table
-- =========================================
CREATE TABLE gtd_projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES gtd_users(id) ON DELETE CASCADE,
    
    -- Project information from Notion
    notion_export_row INTEGER,
    project_name TEXT NOT NULL,
    readings TEXT,
    field_id INTEGER REFERENCES gtd_fields(id),
    keywords TEXT,
    
    -- Relationships
    mother_project TEXT,
    related_projects TEXT,
    related_mother_projects TEXT,
    related_knowledge_vault TEXT,
    related_tasks TEXT,
    
    -- Status
    done_at TIMESTAMP, -- NULL = not done, timestamp = when completed
    do_this_week BOOLEAN DEFAULT FALSE,
    
    -- Additional fields
    gtd_processes TEXT,
    add_checkboxes TEXT,
    source_file VARCHAR(255),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- =========================================
-- Step 5: Create GTD Tasks table
-- =========================================
CREATE TABLE gtd_tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES gtd_users(id) ON DELETE CASCADE,
    
    -- Task information from Notion
    notion_export_row INTEGER,
    task_name TEXT NOT NULL,
    project_id INTEGER REFERENCES gtd_projects(id) ON DELETE SET NULL,
    project_reference TEXT,
    
    -- Status flags
    done_at TIMESTAMP, -- NULL = not done, timestamp = when completed
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
    field_id INTEGER REFERENCES gtd_fields(id),
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

-- =========================================
-- Step 6: Create all indexes
-- =========================================

-- User indexes
CREATE INDEX idx_gtd_users_email ON gtd_users(email_address);
CREATE INDEX idx_gtd_users_active ON gtd_users(is_active);

-- Project indexes
CREATE INDEX idx_gtd_projects_user_id ON gtd_projects(user_id);
CREATE INDEX idx_gtd_projects_field_id ON gtd_projects(field_id);
CREATE INDEX idx_gtd_projects_done_at ON gtd_projects(done_at);

-- Task indexes
CREATE INDEX idx_gtd_tasks_user_id ON gtd_tasks(user_id);
CREATE INDEX idx_gtd_tasks_project_id ON gtd_tasks(project_id);
CREATE INDEX idx_gtd_tasks_field_id ON gtd_tasks(field_id);
CREATE INDEX idx_gtd_tasks_done_at ON gtd_tasks(done_at);
CREATE INDEX idx_gtd_tasks_do_today ON gtd_tasks(do_today);
CREATE INDEX idx_gtd_tasks_do_this_week ON gtd_tasks(do_this_week);

-- =========================================
-- Step 7: Create update triggers
-- =========================================

-- Users update trigger
CREATE OR REPLACE FUNCTION update_gtd_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_gtd_users_updated_at
    BEFORE UPDATE ON gtd_users
    FOR EACH ROW
    EXECUTE FUNCTION update_gtd_users_updated_at();

-- Projects update trigger
CREATE OR REPLACE FUNCTION update_gtd_projects_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_gtd_projects_updated_at
    BEFORE UPDATE ON gtd_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_gtd_projects_updated_at();

-- Tasks update trigger
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

-- =========================================
-- Step 8: Create useful views
-- =========================================

-- Projects with field names
CREATE OR REPLACE VIEW gtd_projects_with_fields AS
SELECT 
    p.*,
    f.name as field_name,
    f.description as field_description,
    CASE WHEN p.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id;

-- Tasks with project and field details
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

-- User dashboard summary
CREATE OR REPLACE VIEW gtd_user_dashboard AS
SELECT 
    u.id as user_id,
    u.first_name,
    u.last_name,
    u.email_address,
    
    -- Project statistics
    COUNT(DISTINCT p.id) as total_projects,
    COUNT(DISTINCT CASE WHEN p.done_at IS NOT NULL THEN p.id END) as completed_projects,
    COUNT(DISTINCT CASE WHEN p.done_at IS NULL THEN p.id END) as active_projects,
    
    -- Task statistics
    COUNT(DISTINCT t.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN t.done_at IS NOT NULL THEN t.id END) as completed_tasks,
    COUNT(DISTINCT CASE WHEN t.done_at IS NULL THEN t.id END) as pending_tasks,
    COUNT(DISTINCT CASE WHEN t.do_today = true AND t.done_at IS NULL THEN t.id END) as tasks_today,
    COUNT(DISTINCT CASE WHEN t.do_this_week = true AND t.done_at IS NULL THEN t.id END) as tasks_this_week,
    
    -- User activity
    u.last_login_at,
    u.created_at as user_since
    
FROM gtd_users u
LEFT JOIN gtd_projects p ON u.id = p.user_id AND p.deleted_at IS NULL
LEFT JOIN gtd_tasks t ON u.id = t.user_id AND t.deleted_at IS NULL
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.first_name, u.last_name, u.email_address, u.last_login_at, u.created_at;

-- =========================================
-- Step 9: Insert Johannes Köppern as first user
-- =========================================
INSERT INTO gtd_users (
    id,
    first_name, 
    last_name, 
    email_address,
    timezone,
    email_verified,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'Johannes',
    'Köppern',
    'johannes.koeppern@googlemail.com',
    'Europe/Berlin',
    true,
    true
);

-- =========================================
-- DONE! Ready for data import
-- =========================================
-- Run this script in Supabase SQL Editor
-- Then run the ETL scripts to import your Notion data