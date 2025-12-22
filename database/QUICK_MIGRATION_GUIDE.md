# 🚨 Quick Migration Guide - Supabase Dashboard

## Masalah yang Terjadi

Script `run_migration.py` gagal connect karena DNS resolution issue:
```
✗ Failed to connect to database: could not translate host name 
  "db.ujwqvweresyqvdmjidlr.supabase.co" to address: No such host is known.
```

**Penyebab:**
- Network/DNS issue (IPv6 vs IPv4)
- Firewall/Antivirus blocking
- ISP blocking Supabase domain

---

## ✅ Solusi Tercepat: Gunakan Supabase Dashboard

Karena ada network issue, cara termudah adalah run migration langsung via Supabase Dashboard.

### **Step-by-Step:**

#### **1. Login ke Supabase**
- Buka: https://app.supabase.com
- Login dengan akun Anda
- Pilih project: `ujwqvweresyqvdmjidlr`

#### **2. Buka SQL Editor**
- Klik menu **"SQL Editor"** di sidebar kiri
- Klik **"New Query"**

#### **3. Run Migration Files (URUTAN PENTING!)**

**Migration 1: Create Users Table**
- Copy seluruh isi file: `database/migrations/001_create_users_table.sql`
- Paste ke SQL Editor
- Klik **"Run"** atau tekan `Ctrl+Enter`
- Tunggu sampai muncul "Success"

**Migration 2: Create Stroke Screenings Table**
- Copy seluruh isi file: `database/migrations/002_create_stroke_screenings_table.sql`
- Paste ke SQL Editor (buat query baru atau replace yang lama)
- Klik **"Run"**
- Tunggu sampai "Success"

**Migration 3: Create Indexes and Views**
- Copy seluruh isi file: `database/migrations/003_create_indexes_and_views.sql`
- Paste ke SQL Editor
- Klik **"Run"**
- Tunggu sampai "Success"

#### **4. Run Seed Data**

**Seed Admin User (WAJIB)**
- Copy seluruh isi file: `database/seeds/001_seed_admin_user.sql`
- Paste ke SQL Editor
- Klik **"Run"**
- Anda akan melihat notice: "Admin user created successfully!"

**Seed Sample Data (OPTIONAL - untuk testing)**
- Copy seluruh isi file: `database/seeds/002_seed_sample_data.sql`
- Paste ke SQL Editor
- Klik **"Run"**
- Ini akan create 3 pasien dummy dengan 4 screening records

#### **5. Verifikasi**

**Cek Tables:**
- Klik menu **"Table Editor"** di sidebar
- Anda harus melihat 2 tables:
  - ✅ `users`
  - ✅ `stroke_screenings`

**Cek Data:**
- Klik table `users`
- Anda harus melihat minimal 1 row (admin user)
- Email: `admin@strokeguard.com`

**Cek Views:**
- Kembali ke SQL Editor
- Run query:
  ```sql
  SELECT * FROM user_screening_summary;
  ```
- Jika berhasil, views sudah dibuat

---

## 🔑 Admin Credentials

Setelah migration selesai, Anda bisa login dengan:

```
Email: admin@strokeguard.com
Password: Admin123!
```

⚠️ **PENTING:** Ganti password ini setelah login pertama kali!

---

## 📊 Test Queries

Setelah migration, coba run queries ini untuk test:

### **1. Lihat Semua Users**
```sql
SELECT id, email, full_name, role, created_at 
FROM users;
```

### **2. Lihat Semua Screenings**
```sql
SELECT 
    s.id,
    u.full_name,
    s.age_at_screening,
    s.bmi,
    s.risk_level,
    s.stroke_probability,
    s.created_at
FROM stroke_screenings s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;
```

### **3. Test Functions**
```sql
-- Test calculate age
SELECT get_user_age('1990-05-15');  -- Should return current age

-- Test calculate BMI
SELECT calculate_bmi(170, 70);  -- Should return 24.2

-- Test get risk level
SELECT get_risk_level(0.85);  -- Should return 'High'
SELECT get_risk_level(0.45);  -- Should return 'Medium'
SELECT get_risk_level(0.15);  -- Should return 'Low'
```

### **4. Test Views**
```sql
-- User summary
SELECT * FROM user_screening_summary;

-- Statistics
SELECT * FROM screening_statistics;

-- High risk alerts
SELECT * FROM recent_high_risk_screenings;
```

---

## 🔄 Jika Perlu Rollback

Jika ada kesalahan dan perlu rollback:

```sql
-- Drop everything
DROP VIEW IF EXISTS recent_high_risk_screenings CASCADE;
DROP VIEW IF EXISTS screening_statistics CASCADE;
DROP VIEW IF EXISTS user_screening_summary CASCADE;

DROP FUNCTION IF EXISTS get_risk_level(DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS calculate_bmi(DECIMAL, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS get_user_age(DATE) CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

DROP TABLE IF EXISTS stroke_screenings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS smoking_status CASCADE;
DROP TYPE IF EXISTS residence_type CASCADE;
DROP TYPE IF EXISTS work_type CASCADE;
DROP TYPE IF EXISTS risk_level CASCADE;
DROP TYPE IF EXISTS gender_type CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;
```

Lalu jalankan ulang migrations dari awal.

---

## 🎯 Next Steps Setelah Migration

1. ✅ **Verify** - Pastikan semua tables dan views ada
2. ✅ **Test Login** - Coba login dengan admin credentials
3. ✅ **Integrate Backend** - Connect FastAPI dengan database
4. ✅ **Build API Endpoints** - Create endpoints untuk:
   - Authentication (register, login)
   - Screening (create, get history)
   - Admin dashboard (view patients)
5. ✅ **Connect ML Model** - Integrate prediction dengan database

---

## 💡 Tips

- **Simpan queries** yang sering dipakai di SQL Editor (klik "Save")
- **Gunakan Table Editor** untuk quick view/edit data
- **Check Logs** di menu "Logs" jika ada error
- **Backup data** sebelum experiment (export to CSV)

---

## 🆘 Troubleshooting

**Error: "type already exists"**
- Jalankan rollback script di atas dulu

**Error: "relation already exists"**
- Table sudah ada, skip migration tersebut atau drop dulu

**Error: "permission denied"**
- Pastikan Anda login sebagai owner project

**Data tidak muncul**
- Refresh page
- Cek di SQL Editor dengan SELECT query

---

**Selamat! Database Anda siap digunakan! 🎉**
