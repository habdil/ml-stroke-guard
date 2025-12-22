-- Migration: Create additional indexes and views
-- Description: Indexes untuk optimasi query dan views untuk reporting
-- Created: 2025-12-22

-- ============================================
-- ADDITIONAL INDEXES
-- ============================================

-- Composite index untuk query yang sering digunakan
CREATE INDEX idx_screenings_user_risk ON stroke_screenings(user_id, risk_level);

-- Index untuk filtering berdasarkan tanggal
CREATE INDEX idx_screenings_date_range ON stroke_screenings(created_at) 
WHERE created_at >= CURRENT_DATE - INTERVAL '1 year';

-- ============================================
-- VIEWS FOR REPORTING
-- ============================================

-- View: User dengan jumlah screening
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

COMMENT ON VIEW user_screening_summary IS 'Summary screening per user untuk dashboard admin';

-- View: Statistik screening per risk level
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

COMMENT ON VIEW screening_statistics IS 'Statistik screening berdasarkan risk level';

-- View: Recent high-risk screenings (untuk alert admin)
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

COMMENT ON VIEW recent_high_risk_screenings IS 'Screening berisiko tinggi dalam 30 hari terakhir';

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Get user age
CREATE OR REPLACE FUNCTION get_user_age(birth_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION get_user_age IS 'Menghitung umur dari tanggal lahir';

-- Function: Calculate BMI
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

COMMENT ON FUNCTION calculate_bmi IS 'Menghitung BMI dari tinggi (cm) dan berat (kg)';

-- Function: Get risk level from probability
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

COMMENT ON FUNCTION get_risk_level IS 'Menentukan risk level dari probability (0-1)';
