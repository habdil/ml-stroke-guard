-- Full Database Schema for ML Stroke Guard
-- Description: Complete schema untuk reference
-- Created: 2025-12-22
-- Database: PostgreSQL (Supabase)

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUMS
-- ============================================

-- User role
CREATE TYPE user_role AS ENUM ('ADMIN', 'PATIENT');

-- Gender
CREATE TYPE gender_type AS ENUM ('Male', 'Female');

-- Risk level
CREATE TYPE risk_level AS ENUM ('Low', 'Medium', 'High');

-- Work type
CREATE TYPE work_type AS ENUM (
    'Private',
    'Self-employed',
    'Govt_job',
    'children',
    'Never_worked'
);

-- Residence type
CREATE TYPE residence_type AS ENUM ('Urban', 'Rural');

-- Smoking status
CREATE TYPE smoking_status AS ENUM (
    'formerly smoked',
    'never smoked',
    'smokes',
    'Unknown'
);

-- ============================================
-- TABLES
-- ============================================

-- Users table
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
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_age CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '10 years'),
    CONSTRAINT phone_format CHECK (phone_number IS NULL OR phone_number ~* '^\+?[0-9]{10,15}$')
);

-- Stroke screenings table
CREATE TABLE stroke_screenings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    
    -- Snapshot data
    age_at_screening INTEGER NOT NULL,
    height_cm DECIMAL(5,2) NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    bmi DECIMAL(4,1) NOT NULL,
    
    -- Input data
    hypertension BOOLEAN NOT NULL,
    heart_disease BOOLEAN NOT NULL,
    ever_married BOOLEAN NOT NULL,
    work_type work_type NOT NULL,
    residence_type residence_type NOT NULL,
    avg_glucose_level DECIMAL(6,2) NOT NULL,
    smoking_status smoking_status NOT NULL,
    
    -- Prediction results
    stroke_probability DECIMAL(5,4) NOT NULL,
    risk_level risk_level NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_age CHECK (age_at_screening >= 0 AND age_at_screening <= 120),
    CONSTRAINT valid_height CHECK (height_cm >= 50 AND height_cm <= 250),
    CONSTRAINT valid_weight CHECK (weight_kg >= 20 AND weight_kg <= 300),
    CONSTRAINT valid_bmi CHECK (bmi >= 10 AND bmi <= 60),
    CONSTRAINT valid_glucose CHECK (avg_glucose_level >= 50 AND avg_glucose_level <= 400),
    CONSTRAINT valid_probability CHECK (stroke_probability >= 0 AND stroke_probability <= 1)
);

-- ============================================
-- INDEXES
-- ============================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Screenings indexes
CREATE INDEX idx_screenings_user_id ON stroke_screenings(user_id);
CREATE INDEX idx_screenings_created_at ON stroke_screenings(created_at DESC);
CREATE INDEX idx_screenings_risk_level ON stroke_screenings(risk_level);
CREATE INDEX idx_screenings_user_created ON stroke_screenings(user_id, created_at DESC);
CREATE INDEX idx_screenings_user_risk ON stroke_screenings(user_id, risk_level);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Calculate age function
CREATE OR REPLACE FUNCTION get_user_age(birth_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Calculate BMI function
CREATE OR REPLACE FUNCTION calculate_bmi(height_cm DECIMAL, weight_kg DECIMAL)
RETURNS DECIMAL AS $$
DECLARE
    height_m DECIMAL;
    bmi DECIMAL;
BEGIN
    height_m := height_cm / 100.0;
    bmi := weight_kg / (height_m * height_m);
    RETURN ROUND(bmi, 1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Get risk level function
CREATE OR REPLACE FUNCTION get_risk_level(probability DECIMAL)
RETURNS risk_level AS $$
BEGIN
    IF probability >= 0.7 THEN
        RETURN 'High'::risk_level;
    ELSIF probability >= 0.4 THEN
        RETURN 'Medium'::risk_level;
    ELSE
        RETURN 'Low'::risk_level;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- TRIGGERS
-- ============================================

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stroke_screenings_updated_at
    BEFORE UPDATE ON stroke_screenings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS
-- ============================================

-- User screening summary
CREATE OR REPLACE VIEW user_screening_summary AS
SELECT 
    u.id,
    u.full_name,
    u.email,
    u.date_of_birth,
    u.gender,
    u.role,
    COUNT(s.id) as total_screenings,
    MAX(s.created_at) as last_screening_date,
    MAX(s.risk_level) as highest_risk_level
FROM users u
LEFT JOIN stroke_screenings s ON u.id = s.user_id
WHERE u.role = 'PATIENT'
GROUP BY u.id, u.full_name, u.email, u.date_of_birth, u.gender, u.role;

-- Screening statistics
CREATE OR REPLACE VIEW screening_statistics AS
SELECT 
    risk_level,
    COUNT(*) as total_count,
    ROUND(AVG(age_at_screening), 1) as avg_age,
    ROUND(AVG(bmi), 1) as avg_bmi,
    ROUND(AVG(avg_glucose_level), 1) as avg_glucose,
    ROUND(AVG(stroke_probability)::numeric, 4) as avg_probability,
    COUNT(CASE WHEN hypertension = true THEN 1 END) as hypertension_count,
    COUNT(CASE WHEN heart_disease = true THEN 1 END) as heart_disease_count
FROM stroke_screenings
GROUP BY risk_level
ORDER BY 
    CASE risk_level
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;

-- Recent high-risk screenings
CREATE OR REPLACE VIEW recent_high_risk_screenings AS
SELECT 
    s.id,
    s.user_id,
    u.full_name,
    u.email,
    u.phone_number,
    s.age_at_screening,
    s.bmi,
    s.stroke_probability,
    s.risk_level,
    s.created_at
FROM stroke_screenings s
JOIN users u ON s.user_id = u.id
WHERE s.risk_level = 'High'
  AND s.created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY s.created_at DESC;
