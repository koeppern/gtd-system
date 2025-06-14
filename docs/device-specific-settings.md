# GTD Device-Specific User Settings

## Overview

Implemented a comprehensive device-specific user settings system that stores different configuration values for desktop, tablet, and phone devices. This allows users to have optimized settings for each device type they use.

## Database Structure

### gtd_setting_keys Table

Defines all valid setting keys that can be stored in user settings:

```sql
CREATE TABLE gtd_setting_keys (
    key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    data_type TEXT NOT NULL DEFAULT 'string',
    default_value JSONB,
    category TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Categories of Settings:**
- `ui` - User interface preferences (sidebar, theme, density)
- `table` - Table column configuration (visibility, width, order)
- `pagination` - Page size preferences
- `navigation` - Default views and quick add preferences  
- `dashboard` - Dashboard widget configuration
- `filters` - Filter and grouping preferences
- `notifications` - Toast and alert preferences
- `display` - Date/time format preferences
- `performance` - Performance optimization settings

### gtd_user_settings Table

Stores device-specific settings in a JSONB structure:

```sql
CREATE TABLE gtd_user_settings (
    user_id UUID PRIMARY KEY,
    settings_json JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**JSONB Structure:**
```json
{
  "desktop": {
    "sidebar_open": true,
    "theme_mode": "light",
    "tasks_table_columns": ["task_name", "project_name", "field_name", "priority"],
    "tasks_table_column_widths": {"task_name": 200, "project_name": 150}
  },
  "tablet": {
    "sidebar_open": false,
    "theme_mode": "dark",
    "tasks_table_columns": ["task_name", "priority"]
  },
  "phone": {
    "sidebar_open": false,
    "theme_mode": "dark",
    "tasks_table_columns": ["task_name"]
  }
}
```

## Database Functions

### get_user_setting(user_id, device, setting_key)
Retrieves a setting value with automatic fallback to default:

```sql
SELECT get_user_setting(
  '00000000-0000-0000-0000-000000000001', 
  'desktop', 
  'sidebar_open'
);
```

### set_user_setting(user_id, device, setting_key, setting_value)
Sets a setting value for a specific user and device:

```sql
SELECT set_user_setting(
  '00000000-0000-0000-0000-000000000001',
  'desktop',
  'sidebar_open',
  'false'::jsonb
);
```

## Backend API Endpoints

### Get Settings
```http
# Get all settings for a device
GET /api/users/me/settings?device=desktop

# Get full settings structure
GET /api/users/me/settings

# Get specific setting for device
GET /api/users/me/settings/desktop/sidebar_open

# Get available setting keys
GET /api/users/me/settings/keys
```

### Update Settings
```http
# Update single setting
PUT /api/users/me/settings/desktop/sidebar_open
Content-Type: application/json
false

# Update multiple settings for device
PUT /api/users/me/settings/desktop
Content-Type: application/json
{
  "sidebar_open": false,
  "theme_mode": "dark"
}
```

### Delete Settings
```http
# Reset setting to default
DELETE /api/users/me/settings/desktop/sidebar_open

# Reset all settings to defaults
DELETE /api/users/me/settings
```

## Frontend Implementation

### Device Detection
Automatic device type detection based on screen size:

```typescript
import { useDeviceType, detectDeviceType } from '@/lib/device-utils';

const device = useDeviceType(); // 'desktop' | 'tablet' | 'phone'
```

### API Client
Device-specific settings API:

```typescript
import { api } from '@/lib/api';

// Get settings for current device
const settings = await api.userSettings.getAll('desktop');

// Update setting for current device
await api.userSettings.update('desktop', 'sidebar_open', false);

// Update multiple settings
await api.userSettings.updateDevice('desktop', {
  sidebar_open: false,
  theme_mode: 'dark'
});
```

### Mutation Hooks
Type-safe mutations with cache invalidation:

```typescript
import { useUserSettingsMutations } from '@/hooks/use-mutations';

const { updateSetting, updateDeviceSettings } = useUserSettingsMutations();

// Update single setting
await updateSetting.mutateAsync({
  device: 'desktop',
  key: 'sidebar_open',
  value: false
});

// Update multiple settings
await updateDeviceSettings.mutateAsync({
  device: 'desktop',
  settings: { sidebar_open: false, theme_mode: 'dark' }
});
```

### Table Column Management
Automatically saves column widths and order per device:

```typescript
import { useResizableColumns } from '@/components/ui/resizable-table';

const { columns, handleColumnResize, handleColumnReorder } = useResizableColumns(
  'tasks', // table key
  defaultColumns
);

// Column changes are automatically saved to:
// - tasks_table_columns (array of column keys)
// - tasks_table_column_widths (object with key->width mapping)
```

## Setting Keys Reference

### UI Settings
- `sidebar_open` - Sidebar visibility (boolean)
- `theme_mode` - Color theme: "light" | "dark" | "system"
- `density` - UI density: "compact" | "normal" | "comfortable"
- `animations_enabled` - UI animations enabled (boolean)

### Table Settings
- `tasks_table_columns` - Visible task columns (array of strings)
- `tasks_table_column_widths` - Task column widths (object)
- `projects_table_columns` - Visible project columns (array)
- `projects_table_column_widths` - Project column widths (object)
- `fields_table_columns` - Visible field columns (array)
- `fields_table_column_widths` - Field column widths (object)

### Pagination Settings
- `tasks_page_size` - Tasks per page (number, default: 50)
- `projects_page_size` - Projects per page (number, default: 50)
- `fields_page_size` - Fields per page (number, default: 25)

### Navigation Settings
- `default_tasks_view` - Default tasks view: "active" | "all"
- `default_projects_view` - Default projects view: "active" | "all"
- `quick_add_default_type` - Quick add default: "task" | "project"

### Dashboard Settings
- `dashboard_widgets` - Enabled widgets (array)
- `dashboard_widget_order` - Widget order (array)

### Display Settings
- `date_format` - Date format string (default: "YYYY-MM-DD")
- `time_format` - Time format: "12h" | "24h"
- `show_relative_dates` - Show relative dates (boolean)

## Device-Specific Behaviors

### Desktop (≥1024px)
- Sidebar open by default
- Full column set in tables
- Larger page sizes
- Full dashboard widgets

### Tablet (768-1023px)
- Sidebar collapsed by default
- Reduced column set in tables
- Medium page sizes
- Essential widgets only

### Phone (<768px)
- Sidebar hidden by default
- Minimal column set in tables
- Smaller page sizes
- Compact widget layout

## Migration from Old Settings

The migration automatically:
1. Backs up existing settings to `gtd_user_settings_backup`
2. Creates new table structure
3. Adds validation functions
4. Populates setting keys
5. Sets up helper functions

## Validation

Automatic validation ensures:
- Only valid device categories: "desktop", "tablet", "phone"
- Only registered setting keys from `gtd_setting_keys`
- Proper data types and constraints
- Automatic fallback to defaults

## Cache Integration

Settings are automatically cached and invalidated:
- Immediate cache refresh for UI-critical settings
- Background refresh for less critical settings  
- Device-specific cache keys
- Optimistic updates for better UX

## Usage Examples

### Responsive Table Columns
```typescript
// Desktop: Show all columns
["task_name", "project_name", "field_name", "priority", "do_today", "status"]

// Tablet: Show essential columns
["task_name", "project_name", "priority", "status"]

// Phone: Show minimal columns
["task_name", "status"]
```

### Device-Aware Components
```typescript
const device = useDeviceType();
const sidebarSetting = useSetting(device, 'sidebar_open');

return (
  <AppLayout sidebarOpen={device === 'phone' ? false : sidebarSetting}>
    {/* Content */}
  </AppLayout>
);
```

This system provides a flexible, type-safe, and performant way to manage user preferences across different device types while maintaining data consistency and providing excellent UX.