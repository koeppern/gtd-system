-- Create gtd_setting_keys table to define all valid setting keys
-- This table controls which keys are allowed in the settings_json

CREATE TABLE IF NOT EXISTS gtd_setting_keys (
    key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    data_type TEXT NOT NULL DEFAULT 'string', -- string, boolean, number, array, object
    default_value JSONB,
    category TEXT, -- ui, table, navigation, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add some indexes for better performance
CREATE INDEX IF NOT EXISTS idx_gtd_setting_keys_category ON gtd_setting_keys(category);

-- Insert all valid setting keys based on our GTD application
INSERT INTO gtd_setting_keys (key, description, data_type, default_value, category) VALUES
-- UI/Layout Settings
('sidebar_open', 'Whether the sidebar is open/collapsed', 'boolean', 'true', 'ui'),
('theme_mode', 'Color theme preference (light/dark/system)', 'string', '"system"', 'ui'),
('density', 'UI density (compact/normal/comfortable)', 'string', '"normal"', 'ui'),
('animations_enabled', 'Whether UI animations are enabled', 'boolean', 'true', 'ui'),

-- Table Settings  
('tasks_table_columns', 'Visible columns and order for tasks table', 'array', '["task_name", "project_name", "field_name", "priority", "do_today"]', 'table'),
('tasks_table_column_widths', 'Column widths for tasks table', 'object', '{}', 'table'),
('projects_table_columns', 'Visible columns and order for projects table', 'array', '["project_name", "field_name", "status", "task_count", "do_this_week"]', 'table'),
('projects_table_column_widths', 'Column widths for projects table', 'object', '{}', 'table'),
('fields_table_columns', 'Visible columns and order for fields table', 'array', '["field_name", "description", "created_at"]', 'table'),
('fields_table_column_widths', 'Column widths for fields table', 'object', '{}', 'table'),

-- Pagination Settings
('tasks_page_size', 'Number of tasks to show per page', 'number', '50', 'pagination'),
('projects_page_size', 'Number of projects to show per page', 'number', '50', 'pagination'),
('fields_page_size', 'Number of fields to show per page', 'number', '25', 'pagination'),

-- Navigation/View Settings
('default_tasks_view', 'Default view when opening tasks (active/all)', 'string', '"active"', 'navigation'),
('default_projects_view', 'Default view when opening projects (active/all)', 'string', '"active"', 'navigation'),
('quick_add_default_type', 'Default type for quick add (task/project)', 'string', '"task"', 'navigation'),

-- Dashboard Settings
('dashboard_widgets', 'Enabled widgets on dashboard', 'array', '["today_tasks", "overdue_tasks", "project_progress", "field_distribution"]', 'dashboard'),
('dashboard_widget_order', 'Order of widgets on dashboard', 'array', '["today_tasks", "overdue_tasks", "project_progress", "field_distribution"]', 'dashboard'),

-- Filter/Search Settings
('remember_filters', 'Whether to remember filter state between sessions', 'boolean', 'true', 'filters'),
('default_task_grouping', 'Default grouping for tasks', 'string', 'null', 'filters'),
('default_project_grouping', 'Default grouping for projects', 'string', 'null', 'filters'),

-- Notification Settings
('show_completion_toasts', 'Show toast notifications for task/project completion', 'boolean', 'true', 'notifications'),
('show_error_toasts', 'Show toast notifications for errors', 'boolean', 'true', 'notifications'),
('show_success_toasts', 'Show toast notifications for successful actions', 'boolean', 'true', 'notifications'),

-- Data Display Settings
('date_format', 'Preferred date format', 'string', '"YYYY-MM-DD"', 'display'),
('time_format', 'Preferred time format (12h/24h)', 'string', '"24h"', 'display'),
('show_relative_dates', 'Show relative dates (e.g. "2 days ago")', 'boolean', 'true', 'display'),

-- Performance Settings  
('enable_animations', 'Enable UI animations', 'boolean', 'true', 'performance'),
('preload_data', 'Preload data for better performance', 'boolean', 'true', 'performance'),
('cache_duration', 'Cache duration in minutes', 'number', '10', 'performance');

-- Add a comment explaining the table structure
COMMENT ON TABLE gtd_setting_keys IS 'Defines all valid setting keys that can be stored in gtd_user_settings.settings_json. This ensures data consistency and provides validation for user settings.';
COMMENT ON COLUMN gtd_setting_keys.key IS 'Unique setting key name used in settings_json';
COMMENT ON COLUMN gtd_setting_keys.description IS 'Human-readable description of what this setting controls';
COMMENT ON COLUMN gtd_setting_keys.data_type IS 'Expected data type: string, boolean, number, array, object';
COMMENT ON COLUMN gtd_setting_keys.default_value IS 'Default value as JSONB (used when setting is not explicitly set)';
COMMENT ON COLUMN gtd_setting_keys.category IS 'Category for grouping related settings';