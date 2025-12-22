-- Seed: Sample data untuk testing
-- Description: Data dummy untuk testing aplikasi
-- Created: 2025-12-22
-- NOTE: File ini OPTIONAL, hanya untuk development/testing

-- Insert sample patients
INSERT INTO users (
    email,
    password,
    full_name,
    date_of_birth,
    gender,
    phone_number,
    role
) VALUES 
(
    'patient1@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQC0mQ0Gy', -- Admin123!
    'Budi Santoso',
    '1985-05-15',
    'Male',
    '+6281234567891',
    'PATIENT'
),
(
    'patient2@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQC0mQ0Gy', -- Admin123!
    'Siti Nurhaliza',
    '1992-08-20',
    'Female',
    '+6281234567892',
    'PATIENT'
),
(
    'patient3@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQC0mQ0Gy', -- Admin123!
    'Ahmad Hidayat',
    '1978-12-10',
    'Male',
    '+6281234567893',
    'PATIENT'
)
ON CONFLICT (email) DO NOTHING;

-- Insert sample screenings
-- Get user IDs first
DO $$
DECLARE
    patient1_id UUID;
    patient2_id UUID;
    patient3_id UUID;
BEGIN
    -- Get patient IDs
    SELECT id INTO patient1_id FROM users WHERE email = 'patient1@example.com';
    SELECT id INTO patient2_id FROM users WHERE email = 'patient2@example.com';
    SELECT id INTO patient3_id FROM users WHERE email = 'patient3@example.com';
    
    -- Insert screening for patient 1 (Low Risk)
    INSERT INTO stroke_screenings (
        user_id,
        age_at_screening,
        height_cm,
        weight_kg,
        bmi,
        hypertension,
        heart_disease,
        ever_married,
        work_type,
        residence_type,
        avg_glucose_level,
        smoking_status,
        stroke_probability,
        risk_level
    ) VALUES (
        patient1_id,
        39,
        170.0,
        70.0,
        24.2,
        false,
        false,
        true,
        'Private',
        'Urban',
        95.5,
        'never smoked',
        0.15,
        'Low'
    );
    
    -- Insert screening for patient 2 (Medium Risk)
    INSERT INTO stroke_screenings (
        user_id,
        age_at_screening,
        height_cm,
        weight_kg,
        bmi,
        hypertension,
        heart_disease,
        ever_married,
        work_type,
        residence_type,
        avg_glucose_level,
        smoking_status,
        stroke_probability,
        risk_level
    ) VALUES (
        patient2_id,
        32,
        160.0,
        65.0,
        25.4,
        true,
        false,
        true,
        'Self-employed',
        'Urban',
        110.0,
        'never smoked',
        0.45,
        'Medium'
    );
    
    -- Insert screening for patient 3 (High Risk)
    INSERT INTO stroke_screenings (
        user_id,
        age_at_screening,
        height_cm,
        weight_kg,
        bmi,
        hypertension,
        heart_disease,
        ever_married,
        work_type,
        residence_type,
        avg_glucose_level,
        smoking_status,
        stroke_probability,
        risk_level
    ) VALUES (
        patient3_id,
        46,
        175.0,
        95.0,
        31.0,
        true,
        true,
        true,
        'Govt_job',
        'Rural',
        180.5,
        'smokes',
        0.85,
        'High'
    );
    
    -- Insert second screening for patient 3 (showing improvement)
    INSERT INTO stroke_screenings (
        user_id,
        age_at_screening,
        height_cm,
        weight_kg,
        bmi,
        hypertension,
        heart_disease,
        ever_married,
        work_type,
        residence_type,
        avg_glucose_level,
        smoking_status,
        stroke_probability,
        risk_level,
        created_at
    ) VALUES (
        patient3_id,
        46,
        175.0,
        88.0,
        28.7,
        true,
        true,
        true,
        'Govt_job',
        'Rural',
        150.0,
        'formerly smoked',
        0.65,
        'Medium',
        NOW() - INTERVAL '15 days'
    );
    
    RAISE NOTICE 'Sample data inserted successfully!';
    RAISE NOTICE 'Created 3 patients with 4 screenings';
END $$;
