-- Migration: Create users table
-- Description: Tabel untuk menyimpan data user (Admin & Pasien)
-- Created: 2025-12-22

-- Enable UUID extension (jika belum ada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM for user role
CREATE TYPE user_role AS ENUM ('ADMIN', 'PATIENT');

-- Create ENUM for gender
CREATE TYPE gender_type AS ENUM ('Male', 'Female');

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_type NOT NULL,
    phone_number VARCHAR(20),
    role user_role NOT NULL DEFAULT 'PATIENT',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_age CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '10 years'),
    CONSTRAINT phone_format CHECK (phone_number IS NULL OR phone_number ~* '^\+?[0-9]{10,15}$')
);

-- Create index for faster queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE users IS 'Tabel untuk menyimpan data user (Admin & Pasien)';
COMMENT ON COLUMN users.id IS 'Unique identifier untuk user';
COMMENT ON COLUMN users.email IS 'Email untuk login (unique)';
COMMENT ON COLUMN users.password IS 'Password yang sudah di-hash (bcrypt/argon2)';
COMMENT ON COLUMN users.full_name IS 'Nama lengkap user';
COMMENT ON COLUMN users.date_of_birth IS 'Tanggal lahir (untuk kalkulasi umur)';
COMMENT ON COLUMN users.gender IS 'Jenis kelamin (Male/Female)';
COMMENT ON COLUMN users.phone_number IS 'Nomor telepon (optional)';
COMMENT ON COLUMN users.role IS 'Role user (ADMIN/PATIENT)';
