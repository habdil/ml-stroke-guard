-- Seed: Create default admin user
-- Description: Membuat user admin default untuk akses pertama kali
-- Created: 2025-12-22
-- Password default: Admin123! (HARUS DIGANTI setelah login pertama!)

-- Insert admin user
-- NOTE: Password ini adalah hash dari "Admin123!" menggunakan bcrypt
-- Anda HARUS mengganti password ini setelah login pertama!
INSERT INTO users (
    email,
    password,
    full_name,
    date_of_birth,
    gender,
    phone_number,
    role
) VALUES (
    'admin@strokeguard.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQC0mQ0Gy', -- Admin123!
    'Administrator',
    '1990-01-01',
    'Male',
    '+6281234567890',
    'ADMIN'
)
ON CONFLICT (email) DO NOTHING;

-- Verify insertion
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM users WHERE email = 'admin@strokeguard.com') THEN
        RAISE NOTICE 'Admin user created successfully!';
        RAISE NOTICE 'Email: admin@strokeguard.com';
        RAISE NOTICE 'Password: Admin123!';
        RAISE NOTICE 'IMPORTANT: Please change this password after first login!';
    ELSE
        RAISE NOTICE 'Admin user already exists, skipping...';
    END IF;
END $$;
