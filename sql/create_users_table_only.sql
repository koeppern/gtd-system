-- =========================================
-- CREATE GTD USERS TABLE ONLY
-- =========================================
-- Simple script to create just the missing gtd_users table

-- Create GTD Users table
CREATE TABLE IF NOT EXISTS gtd_users (
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

-- Create index
CREATE INDEX IF NOT EXISTS idx_gtd_users_email ON gtd_users(email_address);
CREATE INDEX IF NOT EXISTS idx_gtd_users_active ON gtd_users(is_active);

-- Insert Johannes Köppern as first user
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
) ON CONFLICT (id) DO NOTHING;

-- Success message
SELECT 'GTD Users table created and Johannes Köppern added successfully!' as result;