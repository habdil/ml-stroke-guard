# Database Migration Guide - ML Stroke Guard

## 📋 Overview

Folder ini berisi semua file migration dan seed data untuk database ML Stroke Guard menggunakan **PostgreSQL (Supabase)**.

## 📁 Struktur Folder

```
database/
├── migrations/
│   ├── 001_create_users_table.sql
│   ├── 002_create_stroke_screenings_table.sql
│   └── 003_create_indexes_and_views.sql
├── seeds/
│   ├── 001_seed_admin_user.sql
│   └── 002_seed_sample_data.sql (optional)
├── schema.sql (full schema untuk reference)
└── README.md (file ini)
```

---

## 🗄️ Database Schema

### **Tabel 1: `users`**
Menyimpan data user (Admin & Pasien)

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | VARCHAR(255) | Email login (unique) |
| `password` | VARCHAR(255) | Hashed password |
| `full_name` | VARCHAR(255) | Nama lengkap |
| `date_of_birth` | DATE | Tanggal lahir |
| `gender` | ENUM | 'Male' atau 'Female' |
| `phone_number` | VARCHAR(20) | Nomor telepon (optional) |
| `role` | ENUM | 'ADMIN' atau 'PATIENT' |
| `created_at` | TIMESTAMP | Waktu registrasi |
| `updated_at` | TIMESTAMP | Waktu update terakhir |

### **Tabel 2: `stroke_screenings`**
Menyimpan hasil screening/prediction stroke

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key ke users |
| `age_at_screening` | INTEGER | Umur saat screening |
| `height_cm` | DECIMAL(5,2) | Tinggi badan (cm) |
| `weight_kg` | DECIMAL(5,2) | Berat badan (kg) |
| `bmi` | DECIMAL(4,1) | Body Mass Index |
| `hypertension` | BOOLEAN | Riwayat hipertensi |
| `heart_disease` | BOOLEAN | Riwayat penyakit jantung |
| `ever_married` | BOOLEAN | Status pernikahan |
| `work_type` | ENUM | Jenis pekerjaan |
| `residence_type` | ENUM | 'Urban' atau 'Rural' |
| `avg_glucose_level` | DECIMAL(6,2) | Rata-rata kadar glukosa |
| `smoking_status` | ENUM | Status merokok |
| `stroke_probability` | DECIMAL(5,4) | Probabilitas stroke (0-1) |
| `risk_level` | ENUM | 'Low', 'Medium', 'High' |
| `created_at` | TIMESTAMP | Waktu screening |
| `updated_at` | TIMESTAMP | Waktu update |

---

## 🚀 Cara Menjalankan Migration

### **Opsi 1: Via Supabase Dashboard (Recommended)**

1. **Login ke Supabase Dashboard**
   - Buka https://app.supabase.com
   - Pilih project Anda

2. **Buka SQL Editor**
   - Klik menu "SQL Editor" di sidebar
   - Klik "New Query"

3. **Jalankan Migration Secara Berurutan**
   
   **Step 1:** Copy & paste isi file `migrations/001_create_users_table.sql`
   ```sql
   -- Paste konten file 001_create_users_table.sql
   ```
   Klik "Run" atau tekan `Ctrl+Enter`

   **Step 2:** Copy & paste isi file `migrations/002_create_stroke_screenings_table.sql`
   ```sql
   -- Paste konten file 002_create_stroke_screenings_table.sql
   ```
   Klik "Run"

   **Step 3:** Copy & paste isi file `migrations/003_create_indexes_and_views.sql`
   ```sql
   -- Paste konten file 003_create_indexes_and_views.sql
   ```
   Klik "Run"

4. **Jalankan Seed Data (Optional)**
   
   **Seed Admin User (WAJIB):**
   ```sql
   -- Paste konten file seeds/001_seed_admin_user.sql
   ```
   
   **Seed Sample Data (OPTIONAL - untuk testing):**
   ```sql
   -- Paste konten file seeds/002_seed_sample_data.sql
   ```

5. **Verifikasi**
   - Klik menu "Table Editor"
   - Pastikan tabel `users` dan `stroke_screenings` sudah ada
   - Cek data admin di tabel `users`

---

### **Opsi 2: Via psql CLI**

Jika Anda prefer menggunakan command line:

```bash
# 1. Connect ke Supabase database
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# 2. Jalankan migrations
\i database/migrations/001_create_users_table.sql
\i database/migrations/002_create_stroke_screenings_table.sql
\i database/migrations/003_create_indexes_and_views.sql

# 3. Jalankan seeds
\i database/seeds/001_seed_admin_user.sql
\i database/seeds/002_seed_sample_data.sql

# 4. Verifikasi
\dt  -- List semua tables
\dv  -- List semua views
SELECT * FROM users;
```

---

### **Opsi 3: Via Python Script**

Buat file `run_migration.py`:

```python
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv('SUPABASE_HOST'),
    database=os.getenv('SUPABASE_DB'),
    user=os.getenv('SUPABASE_USER'),
    password=os.getenv('SUPABASE_PASSWORD'),
    port=os.getenv('SUPABASE_PORT', 5432)
)

cursor = conn.cursor()

# Migration files
migration_files = [
    'database/migrations/001_create_users_table.sql',
    'database/migrations/002_create_stroke_screenings_table.sql',
    'database/migrations/003_create_indexes_and_views.sql',
]

# Seed files
seed_files = [
    'database/seeds/001_seed_admin_user.sql',
    # 'database/seeds/002_seed_sample_data.sql',  # Uncomment jika perlu
]

# Run migrations
print("Running migrations...")
for file_path in migration_files:
    print(f"Executing {file_path}...")
    with open(file_path, 'r') as f:
        sql = f.read()
        cursor.execute(sql)
        conn.commit()
    print(f"✓ {file_path} executed successfully")

# Run seeds
print("\nRunning seeds...")
for file_path in seed_files:
    print(f"Executing {file_path}...")
    with open(file_path, 'r') as f:
        sql = f.read()
        cursor.execute(sql)
        conn.commit()
    print(f"✓ {file_path} executed successfully")

print("\n✅ All migrations completed successfully!")

cursor.close()
conn.close()
```

Jalankan:
```bash
python run_migration.py
```

---

## 🔐 Default Admin Credentials

Setelah menjalankan seed, Anda bisa login dengan:

```
Email: admin@strokeguard.com
Password: Admin123!
```

⚠️ **PENTING:** Segera ganti password ini setelah login pertama kali!

---

## 📊 Views yang Tersedia

### 1. `user_screening_summary`
Summary screening per user untuk dashboard admin

```sql
SELECT * FROM user_screening_summary;
```

### 2. `screening_statistics`
Statistik screening berdasarkan risk level

```sql
SELECT * FROM screening_statistics;
```

### 3. `recent_high_risk_screenings`
Screening berisiko tinggi dalam 30 hari terakhir

```sql
SELECT * FROM recent_high_risk_screenings;
```

---

## 🛠️ Utility Functions

### 1. `get_user_age(birth_date)`
Menghitung umur dari tanggal lahir

```sql
SELECT get_user_age('1990-05-15');  -- Returns: 34
```

### 2. `calculate_bmi(height_cm, weight_kg)`
Menghitung BMI

```sql
SELECT calculate_bmi(170, 70);  -- Returns: 24.2
```

### 3. `get_risk_level(probability)`
Menentukan risk level dari probability

```sql
SELECT get_risk_level(0.85);  -- Returns: 'High'
SELECT get_risk_level(0.45);  -- Returns: 'Medium'
SELECT get_risk_level(0.15);  -- Returns: 'Low'
```

---

## 🔄 Rollback Migration

Jika perlu rollback, jalankan:

```sql
-- Drop views
DROP VIEW IF EXISTS recent_high_risk_screenings;
DROP VIEW IF EXISTS screening_statistics;
DROP VIEW IF EXISTS user_screening_summary;

-- Drop functions
DROP FUNCTION IF EXISTS get_risk_level(DECIMAL);
DROP FUNCTION IF EXISTS calculate_bmi(DECIMAL, DECIMAL);
DROP FUNCTION IF EXISTS get_user_age(DATE);
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables (CASCADE akan drop foreign keys juga)
DROP TABLE IF EXISTS stroke_screenings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop types
DROP TYPE IF EXISTS smoking_status;
DROP TYPE IF EXISTS residence_type;
DROP TYPE IF EXISTS work_type;
DROP TYPE IF EXISTS risk_level;
DROP TYPE IF EXISTS gender_type;
DROP TYPE IF EXISTS user_role;
```

---

## 📝 Notes

1. **Urutan Penting:** Jalankan migration files sesuai urutan (001, 002, 003)
2. **Foreign Keys:** Tabel `stroke_screenings` memiliki foreign key ke `users`, jadi `users` harus dibuat dulu
3. **ENUM Types:** Pastikan ENUM types dibuat sebelum tabel yang menggunakannya
4. **Indexes:** Sudah dibuat untuk optimasi query, terutama untuk foreign keys dan filtering
5. **Triggers:** Auto-update `updated_at` sudah dihandle oleh trigger

---

## 🆘 Troubleshooting

### Error: "type already exists"
```sql
-- Gunakan DROP TYPE IF EXISTS sebelum CREATE TYPE
DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM ('ADMIN', 'PATIENT');
```

### Error: "relation already exists"
```sql
-- Gunakan DROP TABLE IF EXISTS
DROP TABLE IF EXISTS users CASCADE;
```

### Error: "permission denied"
Pastikan Anda menggunakan user dengan privilege yang cukup (biasanya `postgres` user di Supabase)

---

## 📞 Support

Jika ada masalah saat migration, cek:
1. Supabase project status (pastikan tidak down)
2. Database connection string di `.env`
3. User permissions
4. Error logs di Supabase Dashboard > Logs

---

**Created:** 2025-12-22  
**Database:** PostgreSQL (Supabase)  
**Version:** 1.0.0
