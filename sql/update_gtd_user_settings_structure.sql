-- Update gtd_user_settings table to support device-specific settings
-- This migration changes from individual setting keys to a single JSONB structure

-- First, backup existing data if the table exists
DO $$ 
BEGIN
    -- Check if old structure exists and backup data
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'gtd_user_settings' 
               AND column_name = 'setting_key') THEN
        
        -- Create backup table
        CREATE TABLE IF NOT EXISTS gtd_user_settings_backup AS 
        SELECT * FROM gtd_user_settings;
        
        -- Drop the old table
        DROP TABLE gtd_user_settings;
    END IF;
END $$;

-- Create new gtd_user_settings table structure
CREATE TABLE IF NOT EXISTS gtd_user_settings (
    user_id UUID PRIMARY KEY,
    settings_json JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add foreign key constraint to auth.users if auth schema exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth') THEN
        ALTER TABLE gtd_user_settings 
        ADD CONSTRAINT fk_gtd_user_settings_user_id 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        -- Constraint already exists, ignore
        NULL;
END $$;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_gtd_user_settings_updated_at ON gtd_user_settings(updated_at);
CREATE INDEX IF NOT EXISTS idx_gtd_user_settings_settings_json ON gtd_user_settings USING GIN(settings_json);

-- Add trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_gtd_user_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_gtd_user_settings_updated_at ON gtd_user_settings;
CREATE TRIGGER tr_gtd_user_settings_updated_at
    BEFORE UPDATE ON gtd_user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_gtd_user_settings_updated_at();

-- Add validation function to ensure settings_json only contains valid keys
CREATE OR REPLACE FUNCTION validate_gtd_user_settings()
RETURNS TRIGGER AS $$
DECLARE
    device_key TEXT;
    setting_key TEXT;
    valid_keys TEXT[];
    device_settings JSONB;
BEGIN
    -- Get all valid setting keys
    SELECT ARRAY(SELECT key FROM gtd_setting_keys) INTO valid_keys;
    
    -- Validate each device category (desktop, tablet, phone)
    FOR device_key IN SELECT jsonb_object_keys(NEW.settings_json) LOOP
        IF device_key NOT IN ('desktop', 'tablet', 'phone') THEN
            RAISE EXCEPTION 'Invalid device category: %. Must be one of: desktop, tablet, phone', device_key;
        END IF;
        
        device_settings := NEW.settings_json->device_key;
        
        -- Validate each setting key within the device category
        FOR setting_key IN SELECT jsonb_object_keys(device_settings) LOOP
            IF setting_key != ALL(valid_keys) THEN
                RAISE EXCEPTION 'Invalid setting key: % for device: %. Valid keys are: %', 
                    setting_key, device_key, array_to_string(valid_keys, ', ');
            END IF;
        END LOOP;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add validation trigger
DROP TRIGGER IF EXISTS tr_validate_gtd_user_settings ON gtd_user_settings;
CREATE TRIGGER tr_validate_gtd_user_settings
    BEFORE INSERT OR UPDATE ON gtd_user_settings
    FOR EACH ROW
    EXECUTE FUNCTION validate_gtd_user_settings();

-- Create helper function to get setting value with fallback to default
CREATE OR REPLACE FUNCTION get_user_setting(
    p_user_id UUID,
    p_device TEXT DEFAULT 'desktop',
    p_setting_key TEXT
) RETURNS JSONB AS $$
DECLARE
    setting_value JSONB;
    default_value JSONB;
BEGIN
    -- Get setting value from user settings
    SELECT settings_json->p_device->p_setting_key 
    INTO setting_value
    FROM gtd_user_settings 
    WHERE user_id = p_user_id;
    
    -- If not found, get default value
    IF setting_value IS NULL THEN
        SELECT default_value 
        INTO setting_value
        FROM gtd_setting_keys 
        WHERE key = p_setting_key;
    END IF;
    
    RETURN COALESCE(setting_value, 'null'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- Create helper function to set user setting
CREATE OR REPLACE FUNCTION set_user_setting(
    p_user_id UUID,
    p_device TEXT DEFAULT 'desktop',
    p_setting_key TEXT,
    p_setting_value JSONB
) RETURNS VOID AS $$
DECLARE
    current_settings JSONB;
BEGIN
    -- Validate setting key exists
    IF NOT EXISTS (SELECT 1 FROM gtd_setting_keys WHERE key = p_setting_key) THEN
        RAISE EXCEPTION 'Invalid setting key: %', p_setting_key;
    END IF;
    
    -- Validate device category
    IF p_device NOT IN ('desktop', 'tablet', 'phone') THEN
        RAISE EXCEPTION 'Invalid device category: %. Must be one of: desktop, tablet, phone', p_device;
    END IF;
    
    -- Get current settings or initialize empty
    SELECT COALESCE(settings_json, '{}'::jsonb) 
    INTO current_settings
    FROM gtd_user_settings 
    WHERE user_id = p_user_id;
    
    -- If no settings exist, initialize with empty object
    IF current_settings IS NULL THEN
        current_settings := '{}'::jsonb;
    END IF;
    
    -- Ensure device category exists
    IF NOT (current_settings ? p_device) THEN
        current_settings := jsonb_set(current_settings, ARRAY[p_device], '{}'::jsonb);
    END IF;
    
    -- Set the specific setting
    current_settings := jsonb_set(
        current_settings, 
        ARRAY[p_device, p_setting_key], 
        p_setting_value
    );
    
    -- Insert or update the user settings
    INSERT INTO gtd_user_settings (user_id, settings_json)
    VALUES (p_user_id, current_settings)
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        settings_json = current_settings,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Add comments explaining the new structure
COMMENT ON TABLE gtd_user_settings IS 'Stores user settings in a device-specific JSONB structure. Each user has one row with settings for desktop, tablet, and phone devices.';
COMMENT ON COLUMN gtd_user_settings.user_id IS 'Reference to auth.users.id';
COMMENT ON COLUMN gtd_user_settings.settings_json IS 'JSONB object with structure: {"desktop": {...}, "tablet": {...}, "phone": {...}}';
COMMENT ON FUNCTION get_user_setting IS 'Helper function to get a setting value with fallback to default from gtd_setting_keys';
COMMENT ON FUNCTION set_user_setting IS 'Helper function to set a setting value for a specific device and user';