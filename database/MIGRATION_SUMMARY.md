# 📊 Database Migration Summary - ML Stroke Guard

## ✅ Yang Sudah Dibuat

Saya telah membuat struktur database migration lengkap untuk project Anda:

```
database/
├── migrations/
│   ├── 001_create_users_table.sql           ✓ Tabel users
│   ├── 002_create_stroke_screenings_table.sql ✓ Tabel stroke_screenings
│   └── 003_create_indexes_and_views.sql     ✓ Indexes & Views
├── seeds/
│   ├── 001_seed_admin_user.sql              ✓ Admin default
│   └── 002_seed_sample_data.sql             ✓ Data testing (optional)
├── schema.sql                                ✓ Full schema reference
├── run_migration.py                          ✓ Python migration runner
└── README.md                                 ✓ Dokumentasi lengkap
```

---

## 📋 Database Tables

### **1. Tabel `users`**
**Purpose:** Menyimpan data Admin & Pasien

**Columns:**
- `id` (UUID) - Primary key
- `email` (VARCHAR) - Email login (unique)
- `password` (VARCHAR) - Hashed password
- `full_name` (VARCHAR) - Nama lengkap
- `date_of_birth` (DATE) - **Tanggal lahir** (untuk hitung age otomatis)
- `gender` (ENUM) - 'Male' atau 'Female'
- `phone_number` (VARCHAR) - Nomor telepon (optional)
- `role` (ENUM) - 'ADMIN' atau 'PATIENT'
- `created_at`, `updated_at` (TIMESTAMP)

**Features:**
✅ Email validation (regex)
✅ Age validation (minimal 10 tahun)
✅ Phone format validation
✅ Auto-update timestamp trigger

---

### **2. Tabel `stroke_screenings`**
**Purpose:** Menyimpan hasil screening stroke

**Columns:**

**Snapshot Data:**
- `age_at_screening` (INTEGER) - **Umur saat screening** (calculated & saved)
- `height_cm` (DECIMAL) - **Tinggi badan** (raw data)
- `weight_kg` (DECIMAL) - **Berat badan** (raw data)
- `bmi` (DECIMAL) - **BMI** (calculated & saved)

**Input Screening:**
- `hypertension` (BOOLEAN)
- `heart_disease` (BOOLEAN)
- `ever_married` (BOOLEAN)
- `work_type` (ENUM) - 'Private', 'Self-employed', 'Govt_job', dll
- `residence_type` (ENUM) - 'Urban' atau 'Rural'
- `avg_glucose_level` (DECIMAL)
- `smoking_status` (ENUM) - 'never smoked', 'smokes', dll

**Hasil Prediction:**
- `stroke_probability` (DECIMAL) - Probabilitas 0-1
- `risk_level` (ENUM) - 'Low', 'Medium', 'High'

**Features:**
✅ Foreign key ke `users` (CASCADE delete)
✅ Validasi range untuk semua input
✅ Indexes untuk query cepat
✅ Auto-update timestamp

---

## 🎯 Design Decisions (Sesuai Diskusi)

### **1. Age Management**
❌ **TIDAK** simpan `age` langsung
✅ **Simpan** `date_of_birth` di tabel `users`
✅ **Hitung** age di backend saat screening
✅ **Simpan** `age_at_screening` sebagai snapshot

**Alasan:**
- `date_of_birth` = fakta yang tidak berubah
- `age` = nilai yang berubah setiap tahun
- Snapshot penting untuk historical data

### **2. BMI Management**
❌ **TIDAK** simpan BMI saja
✅ **Simpan** `height_cm` dan `weight_kg` (raw data)
✅ **Hitung** BMI di frontend (untuk preview real-time)
✅ **Hitung ulang** BMI di backend (untuk validasi)
✅ **Simpan** semua (height, weight, BMI)

**Alasan:**
- Height & weight bisa berubah
- User dapat feedback real-time
- Backend validasi untuk security
- Tracking perubahan berat badan

### **3. User Authentication**
✅ **Pasien HARUS login**

**Alasan:**
- Riwayat screening tersimpan
- Data terstruktur untuk admin
- Sesuai standar aplikasi medis
- Lebih baik untuk project akademis

---

## 🚀 Cara Menjalankan Migration

### **Opsi 1: Python Script (Recommended)**

```bash
# 1. Install dependencies
pip install psycopg2-binary python-dotenv

# 2. Setup .env dengan credentials Supabase
# (lihat contoh di bawah)

# 3. Jalankan migration
cd database
python run_migration.py
```

Script akan:
- ✅ Connect ke Supabase
- ✅ Run semua migrations (001, 002, 003)
- ✅ Create admin user
- ✅ (Optional) Insert sample data
- ✅ Verify hasil migration

---

### **Opsi 2: Supabase Dashboard**

1. Login ke https://app.supabase.com
2. Pilih project Anda
3. Buka **SQL Editor**
4. Copy-paste file migration satu per satu:
   - `001_create_users_table.sql`
   - `002_create_stroke_screenings_table.sql`
   - `003_create_indexes_and_views.sql`
   - `seeds/001_seed_admin_user.sql`
5. Run setiap file dengan klik "Run"

---

## 🔐 Environment Variables

Tambahkan ke `.env` Anda:

```env
# Supabase Database (yang sudah ada)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Database Connection (untuk migration)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Atau gunakan individual variables:
SUPABASE_HOST=db.[PROJECT-REF].supabase.co
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-database-password
SUPABASE_PORT=5432
```

**Cara dapat credentials:**
1. Buka Supabase Dashboard
2. Settings > Database
3. Copy **Connection string** atau **Connection pooling**

---

## 🔑 Default Admin Credentials

Setelah migration, login dengan:

```
Email: admin@strokeguard.com
Password: Admin123!
```

⚠️ **PENTING:** Ganti password ini setelah login pertama!

---

## 📊 Bonus Features

### **Views untuk Admin Dashboard:**

1. **`user_screening_summary`** - Summary per user
   ```sql
   SELECT * FROM user_screening_summary;
   ```

2. **`screening_statistics`** - Statistik per risk level
   ```sql
   SELECT * FROM screening_statistics;
   ```

3. **`recent_high_risk_screenings`** - Alert high-risk 30 hari terakhir
   ```sql
   SELECT * FROM recent_high_risk_screenings;
   ```

### **Utility Functions:**

1. **`get_user_age(birth_date)`** - Hitung umur
   ```sql
   SELECT get_user_age('1990-05-15');
   ```

2. **`calculate_bmi(height_cm, weight_kg)`** - Hitung BMI
   ```sql
   SELECT calculate_bmi(170, 70);
   ```

3. **`get_risk_level(probability)`** - Tentukan risk level
   ```sql
   SELECT get_risk_level(0.85);  -- Returns 'High'
   ```

---

## 📝 Next Steps

Setelah migration selesai:

1. ✅ **Test Connection**
   - Coba query `SELECT * FROM users;`
   - Pastikan admin user ada

2. ✅ **Update Backend Code**
   - Integrate dengan FastAPI/Flask
   - Buat endpoints untuk:
     - Auth (register, login)
     - Screening (create, get history)
     - Admin (view all patients)

3. ✅ **Update Frontend**
   - Form register (input date_of_birth)
   - Form screening (input height & weight, auto-calculate BMI)
   - Dashboard admin (view patients & screenings)

4. ✅ **Integrate ML Model**
   - Connect prediction dengan database
   - Save hasil ke `stroke_screenings` table

---

## 🆘 Troubleshooting

**Error: "permission denied"**
- Pastikan menggunakan `postgres` user atau user dengan privilege cukup

**Error: "type already exists"**
- Jalankan rollback dulu (lihat README.md)

**Error: "connection refused"**
- Cek DATABASE_URL di .env
- Pastikan Supabase project aktif

---

## 📞 Support

Baca dokumentasi lengkap di: `database/README.md`

---

**Created:** 2025-12-22  
**Database:** PostgreSQL (Supabase)  
**Tables:** 2 (users, stroke_screenings)  
**Views:** 3 (summary, statistics, alerts)  
**Functions:** 4 (age, bmi, risk_level, update_timestamp)
