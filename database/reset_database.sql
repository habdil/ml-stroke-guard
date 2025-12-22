-- ============================================
-- ML STROKE GUARD - RESET DATABASE
-- ============================================
-- Description: Menghapus SEMUA tables, views, functions, dan types
-- WARNING: Ini akan MENGHAPUS SEMUA DATA!
-- Gunakan dengan hati-hati!
-- ============================================

-- ============================================
-- STEP 1: DROP VIEWS
-- ============================================

DROP VIEW IF EXISTS recent_high_risk_screenings CASCADE;
DROP VIEW IF EXISTS screening_statistics CASCADE;
DROP VIEW IF EXISTS user_screening_summary CASCADE;

-- ============================================
-- STEP 2: DROP FUNCTIONS
-- ============================================

DROP FUNCTION IF EXISTS get_risk_level(DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS calculate_bmi(DECIMAL, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS get_user_age(DATE) CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- ============================================
-- STEP 3: DROP TABLES (CASCADE akan drop foreign keys)
-- ============================================

DROP TABLE IF EXISTS stroke_screenings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- STEP 4: DROP TYPES (ENUM)
-- ============================================

DROP TYPE IF EXISTS smoking_status CASCADE;
DROP TYPE IF EXISTS residence_type CASCADE;
DROP TYPE IF EXISTS work_type CASCADE;
DROP TYPE IF EXISTS risk_level CASCADE;
DROP TYPE IF EXISTS gender_type CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;

-- ============================================
-- VERIFICATION
-- ============================================

-- Check remaining tables (should be empty or only system tables)
SELECT 
    'Remaining Tables:' as info,
    table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Check remaining views (should be empty)
SELECT 
    'Remaining Views:' as info,
    table_name 
FROM information_schema.views 
WHERE table_schema = 'public'
ORDER BY table_name;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'DATABASE RESET COMPLETED!';
    RAISE NOTICE '============================================';
    RAISE NOTICE '';
    RAISE NOTICE 'All tables, views, functions, and types have been dropped.';
    RAISE NOTICE 'Database is now clean and ready for fresh migration.';
    RAISE NOTICE '';
    RAISE NOTICE 'Next step: Run all_in_one_migration.sql to recreate everything';
    RAISE NOTICE '============================================';
END $$;
