-- =========================================
-- APPLY USER SETTINGS UPDATES
-- =========================================
-- This script applies all user settings and field substitution updates

\echo 'Starting user settings and field substitution updates...'

-- 1. Create the gtd_user_settings table
\echo 'Creating gtd_user_settings table...'
\i create_gtd_user_settings_table.sql

-- 2. Create field substitution views
\echo 'Creating field substitution views...'
\i create_field_substitution_views.sql

\echo 'All updates completed successfully!'
\echo ''
\echo 'Summary of changes:'
\echo '- Created gtd_user_settings table with JSONB storage'
\echo '- Added sample table configuration settings'
\echo '- Created views for field_id to field_name substitution'
\echo '- Enhanced views with project names and task counts'
\echo ''
\echo 'Frontend will now:'
\echo '- Store table column widths/order in database instead of localStorage'
\echo '- Use field_name instead of field_id in displays'
\echo '- Persist user preferences across devices and browsers'