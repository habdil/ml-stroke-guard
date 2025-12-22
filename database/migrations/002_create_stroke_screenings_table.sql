-- Migration: Create stroke_screenings table
-- Description: Tabel untuk menyimpan hasil screening/prediction stroke
-- Created: 2025-12-22

-- Create ENUM for risk level
CREATE TYPE risk_level AS ENUM ('Low', 'Medium', 'High');

-- Create ENUM for work type
CREATE TYPE work_type AS ENUM (
    'Private',
    'Self-employed',
    'Govt_job',
    'children',
    'Never_worked'
);

-- Create ENUM for residence type
CREATE TYPE residence_type AS ENUM ('Urban', 'Rural');

-- Create ENUM for smoking status
CREATE TYPE smoking_status AS ENUM (
    'formerly smoked',
    'never smoked',
    'smokes',
    'Unknown'
);

-- Create stroke_screenings table
CREATE TABLE stroke_screenings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    
    -- Snapshot data saat screening
    age_at_screening INTEGER NOT NULL,
    height_cm DECIMAL(5,2) NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    bmi DECIMAL(4,1) NOT NULL,
    
    -- Input data screening
    hypertension BOOLEAN NOT NULL,
    heart_disease BOOLEAN NOT NULL,
    ever_married BOOLEAN NOT NULL,
    work_type work_type NOT NULL,
    residence_type residence_type NOT NULL,
    avg_glucose_level DECIMAL(6,2) NOT NULL,
    smoking_status smoking_status NOT NULL,
    
    -- Hasil prediction
    stroke_probability DECIMAL(5,4) NOT NULL,
    risk_level risk_level NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    
    -- Validation constraints
    CONSTRAINT valid_age CHECK (age_at_screening >= 0 AND age_at_screening <= 120),
    CONSTRAINT valid_height CHECK (height_cm >= 50 AND height_cm <= 250),
    CONSTRAINT valid_weight CHECK (weight_kg >= 20 AND weight_kg <= 300),
    CONSTRAINT valid_bmi CHECK (bmi >= 10 AND bmi <= 60),
    CONSTRAINT valid_glucose CHECK (avg_glucose_level >= 50 AND avg_glucose_level <= 400),
    CONSTRAINT valid_probability CHECK (stroke_probability >= 0 AND stroke_probability <= 1)
);

-- Create indexes for faster queries
CREATE INDEX idx_screenings_user_id ON stroke_screenings(user_id);
CREATE INDEX idx_screenings_created_at ON stroke_screenings(created_at DESC);
CREATE INDEX idx_screenings_risk_level ON stroke_screenings(risk_level);
CREATE INDEX idx_screenings_user_created ON stroke_screenings(user_id, created_at DESC);

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_stroke_screenings_updated_at
    BEFORE UPDATE ON stroke_screenings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE stroke_screenings IS 'Tabel untuk menyimpan hasil screening/prediction stroke';
COMMENT ON COLUMN stroke_screenings.id IS 'Unique identifier untuk screening';
COMMENT ON COLUMN stroke_screenings.user_id IS 'Foreign key ke tabel users';
COMMENT ON COLUMN stroke_screenings.age_at_screening IS 'Umur pasien saat screening (snapshot)';
COMMENT ON COLUMN stroke_screenings.height_cm IS 'Tinggi badan dalam cm';
COMMENT ON COLUMN stroke_screenings.weight_kg IS 'Berat badan dalam kg';
COMMENT ON COLUMN stroke_screenings.bmi IS 'Body Mass Index (calculated)';
COMMENT ON COLUMN stroke_screenings.hypertension IS 'Riwayat hipertensi (true/false)';
COMMENT ON COLUMN stroke_screenings.heart_disease IS 'Riwayat penyakit jantung (true/false)';
COMMENT ON COLUMN stroke_screenings.ever_married IS 'Status pernikahan (true/false)';
COMMENT ON COLUMN stroke_screenings.work_type IS 'Jenis pekerjaan';
COMMENT ON COLUMN stroke_screenings.residence_type IS 'Tipe tempat tinggal (Urban/Rural)';
COMMENT ON COLUMN stroke_screenings.avg_glucose_level IS 'Rata-rata kadar glukosa darah (mg/dL)';
COMMENT ON COLUMN stroke_screenings.smoking_status IS 'Status merokok';
COMMENT ON COLUMN stroke_screenings.stroke_probability IS 'Probabilitas terkena stroke (0-1)';
COMMENT ON COLUMN stroke_screenings.risk_level IS 'Tingkat risiko (Low/Medium/High)';
