-- Migration: Add ML model output fields to stroke_screenings
-- Description: Menambahkan fields untuk menyimpan output lengkap dari ML model
-- Created: 2025-12-22

-- Add new columns to stroke_screenings table
ALTER TABLE stroke_screenings
ADD COLUMN IF NOT EXISTS risk_factors TEXT[], -- Array of risk factors
ADD COLUMN IF NOT EXISTS confidence VARCHAR(20), -- High, Medium, Low
ADD COLUMN IF NOT EXISTS prediction INTEGER, -- 0 or 1
ADD COLUMN IF NOT EXISTS threshold DECIMAL(5,4); -- Optimal threshold used

-- Add comments for documentation
COMMENT ON COLUMN stroke_screenings.risk_factors IS 'Array of identified risk factors (e.g., ["Hypertension", "High BMI"])';
COMMENT ON COLUMN stroke_screenings.confidence IS 'Model confidence level (High/Medium/Low)';
COMMENT ON COLUMN stroke_screenings.prediction IS 'Binary prediction result (0 = Low Risk, 1 = High Risk)';
COMMENT ON COLUMN stroke_screenings.threshold IS 'Optimal threshold used for prediction';

-- Verification
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'MIGRATION COMPLETED SUCCESSFULLY!';
    RAISE NOTICE '============================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Added columns to stroke_screenings:';
    RAISE NOTICE '  - risk_factors (TEXT[])';
    RAISE NOTICE '  - confidence (VARCHAR)';
    RAISE NOTICE '  - prediction (INTEGER)';
    RAISE NOTICE '  - threshold (DECIMAL)';
    RAISE NOTICE '';
    RAISE NOTICE '============================================';
END $$;
