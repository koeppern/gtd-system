CREATE TABLE gtd_users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email_address VARCHAR(255) UNIQUE NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO gtd_users (
    id,
    first_name, 
    last_name, 
    email_address
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Johannes',
    'Köppern',
    'johannes.koeppern@googlemail.com'
);