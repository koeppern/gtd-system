-- =========================================
-- 1. Create GTD Users table
-- =========================================

CREATE TABLE IF NOT EXISTS gtd_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic user information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email_address VARCHAR(255) UNIQUE NOT NULL,
    
    -- User preferences
    timezone VARCHAR(50) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    time_format VARCHAR(10) DEFAULT '24h',
    
    -- GTD-specific settings
    default_field_id INTEGER REFERENCES gtd_fields(id) DEFAULT 1, -- Default to 'Private'
    weekly_review_day INTEGER DEFAULT 0, -- 0=Sunday, 1=Monday, etc.
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- =========================================
-- 2. Create indexes for users table
-- =========================================

CREATE INDEX IF NOT EXISTS idx_gtd_users_email ON gtd_users(email_address);
CREATE INDEX IF NOT EXISTS idx_gtd_users_active ON gtd_users(is_active);
CREATE INDEX IF NOT EXISTS idx_gtd_users_created ON gtd_users(created_at);

-- =========================================
-- 3. Add trigger for auto-update updated_at
-- =========================================

CREATE OR REPLACE FUNCTION update_gtd_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_gtd_users_updated_at ON gtd_users;

CREATE TRIGGER trigger_gtd_users_updated_at
    BEFORE UPDATE ON gtd_users
    FOR EACH ROW
    EXECUTE FUNCTION update_gtd_users_updated_at();

-- =========================================
-- 4. Update existing tables to use proper UUID foreign keys
-- =========================================

-- Note: We're keeping the existing user_id columns as UUID
-- but adding proper foreign key constraints

-- Add foreign key constraint to gtd_projects
DO $$ 
BEGIN
    -- Check if foreign key constraint doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_gtd_projects_user_id' 
        AND table_name = 'gtd_projects'
    ) THEN
        ALTER TABLE gtd_projects 
        ADD CONSTRAINT fk_gtd_projects_user_id 
        FOREIGN KEY (user_id) REFERENCES gtd_users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add foreign key constraint to gtd_tasks
DO $$ 
BEGIN
    -- Check if foreign key constraint doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_gtd_tasks_user_id' 
        AND table_name = 'gtd_tasks'
    ) THEN
        ALTER TABLE gtd_tasks 
        ADD CONSTRAINT fk_gtd_tasks_user_id 
        FOREIGN KEY (user_id) REFERENCES gtd_users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- =========================================
-- 5. Create enhanced views with user information
-- =========================================

-- Enhanced projects view with user info
CREATE OR REPLACE VIEW gtd_projects_with_user_details AS
SELECT 
    p.*,
    f.name as field_name,
    f.description as field_description,
    u.first_name,
    u.last_name,
    u.email_address,
    CASE WHEN p.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id
LEFT JOIN gtd_users u ON p.user_id = u.id;

-- Enhanced tasks view with user info
CREATE OR REPLACE VIEW gtd_tasks_with_user_details AS
SELECT 
    t.*,
    p.project_name,
    p.readings as project_readings,
    f.name as field_name,
    f.description as field_description,
    u.first_name,
    u.last_name,
    u.email_address,
    CASE WHEN t.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_tasks t
LEFT JOIN gtd_projects p ON t.project_id = p.id
LEFT JOIN gtd_fields f ON t.field_id = f.id
LEFT JOIN gtd_users u ON t.user_id = u.id;

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