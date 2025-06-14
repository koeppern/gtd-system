-- Migration script to implement device-specific user settings
-- Run these scripts in order to migrate to the new structure

-- Step 1: Create gtd_setting_keys table
\i create_gtd_setting_keys_table.sql

-- Step 2: Update gtd_user_settings structure  
\i update_gtd_user_settings_structure.sql

-- Step 3: Verify the migration
SELECT 'gtd_setting_keys table' as check_name, 
       count(*) as record_count 
FROM gtd_setting_keys;

SELECT 'gtd_user_settings structure' as check_name,
       column_name,
       data_type
FROM information_schema.columns 
WHERE table_name = 'gtd_user_settings'
ORDER BY ordinal_position;

-- Step 4: Test helper functions
SELECT 'Testing get_user_setting function' as test_name;
SELECT get_user_setting('00000000-0000-0000-0000-000000000001', 'desktop', 'sidebar_open') as default_sidebar_setting;

SELECT 'Testing set_user_setting function' as test_name;
SELECT set_user_setting('00000000-0000-0000-0000-000000000001', 'desktop', 'sidebar_open', 'false'::jsonb);

-- Verify the setting was saved
SELECT 'Verifying setting was saved' as test_name;
SELECT settings_json FROM gtd_user_settings WHERE user_id = '00000000-0000-0000-0000-000000000001';

-- Step 5: Sample data insertion for testing
INSERT INTO gtd_user_settings (user_id, settings_json) VALUES 
('00000000-0000-0000-0000-000000000001', '{
  "desktop": {
    "sidebar_open": true,
    "theme_mode": "light",
    "tasks_table_columns": ["task_name", "project_name", "field_name", "priority", "do_today"],
    "projects_table_columns": ["project_name", "field_name", "status", "task_count"]
  },
  "tablet": {
    "sidebar_open": false,
    "theme_mode": "dark",
    "tasks_table_columns": ["task_name", "project_name", "priority"],
    "projects_table_columns": ["project_name", "status"]
  },
  "phone": {
    "sidebar_open": false,
    "theme_mode": "dark",
    "tasks_table_columns": ["task_name", "priority"],
    "projects_table_columns": ["project_name"]
  }
}'::jsonb)
ON CONFLICT (user_id) DO UPDATE SET 
  settings_json = EXCLUDED.settings_json,
  updated_at = NOW();

-- Step 6: Verify validation works
DO $$
BEGIN
  -- This should fail due to invalid device category
  BEGIN
    INSERT INTO gtd_user_settings (user_id, settings_json) VALUES 
    ('00000000-0000-0000-0000-000000000002', '{"invalid_device": {"test": true}}'::jsonb);
    RAISE EXCEPTION 'Validation should have failed!';
  EXCEPTION 
    WHEN OTHERS THEN
      RAISE NOTICE 'Validation correctly rejected invalid device category: %', SQLERRM;
  END;
  
  -- This should fail due to invalid setting key
  BEGIN
    INSERT INTO gtd_user_settings (user_id, settings_json) VALUES 
    ('00000000-0000-0000-0000-000000000003', '{"desktop": {"invalid_key": true}}'::jsonb);
    RAISE EXCEPTION 'Validation should have failed!';
  EXCEPTION 
    WHEN OTHERS THEN
      RAISE NOTICE 'Validation correctly rejected invalid setting key: %', SQLERRM;
  END;
END $$;

-- Step 7: Show final state
SELECT 'Final verification' as step_name;
SELECT 
  'Setting keys defined' as item,
  count(*) as count
FROM gtd_setting_keys
UNION ALL
SELECT 
  'Users with settings' as item,
  count(*) as count  
FROM gtd_user_settings;

NOTICE 'Migration completed successfully!';
NOTICE 'You can now use the new device-specific settings API endpoints.';
NOTICE 'Example usage:';
NOTICE '  GET /api/users/me/settings?device=desktop';
NOTICE '  PUT /api/users/me/settings/desktop/sidebar_open';
NOTICE '  GET /api/users/me/settings/keys';