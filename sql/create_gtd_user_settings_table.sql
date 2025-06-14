-- =========================================
-- CREATE GTD USER SETTINGS TABLE
-- =========================================
-- This script creates a table to store user interface preferences as JSON

-- First, drop the table if it exists (both old and new names)
DROP TABLE IF EXISTS user_settings CASCADE;
DROP TABLE IF EXISTS gtd_user_settings CASCADE;

-- Create the new gtd_user_settings table
CREATE TABLE gtd_user_settings (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES gtd_users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique settings per user
    UNIQUE(user_id, setting_key)
);

-- Create indexes for performance
CREATE INDEX idx_gtd_user_settings_user_id ON gtd_user_settings(user_id);
CREATE INDEX idx_gtd_user_settings_key ON gtd_user_settings(setting_key);
CREATE INDEX idx_gtd_user_settings_user_key ON gtd_user_settings(user_id, setting_key);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_gtd_user_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic updated_at updates
CREATE TRIGGER trigger_gtd_user_settings_updated_at
    BEFORE UPDATE ON gtd_user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_gtd_user_settings_updated_at();

-- Insert some example settings for default user
INSERT INTO gtd_user_settings (user_id, setting_key, setting_value) VALUES
(
    '00000000-0000-0000-0000-000000000001',
    'table-tasks-widths',
    '{"no": 60, "name": 300, "project": 180, "field": 120, "status": 120, "priority": 100, "do_on_date": 120, "time_expenditure": 100, "reviewed": 90, "url": 100, "created": 120, "updated": 140, "actions": 80}'
),
(
    '00000000-0000-0000-0000-000000000001',
    'table-tasks-order',
    '["no", "name", "project", "field", "status", "priority", "do_on_date", "time_expenditure", "reviewed", "url", "created", "updated", "actions"]'
),
(
    '00000000-0000-0000-0000-000000000001',
    'table-projects-widths',
    '{"no": 60, "name": 300, "field": 120, "status": 120, "tasks": 100, "keywords": 150, "mother_project": 150, "readings": 120, "gtd_processes": 130, "created": 120, "updated": 140, "actions": 80}'
),
(
    '00000000-0000-0000-0000-000000000001',
    'table-projects-order',
    '["no", "name", "field", "status", "tasks", "keywords", "mother_project", "readings", "gtd_processes", "created", "updated", "actions"]'
);

-- Grant permissions
GRANT ALL ON gtd_user_settings TO postgres;
GRANT ALL ON SEQUENCE gtd_user_settings_id_seq TO postgres;

-- Print confirmation
DO $$
BEGIN
    RAISE NOTICE 'GTD User Settings table created successfully!';
    RAISE NOTICE 'Table: gtd_user_settings';
    RAISE NOTICE 'Features: JSONB storage, user_id foreign key, setting_key uniqueness';
    RAISE NOTICE 'Sample settings inserted for default user';
END $$;