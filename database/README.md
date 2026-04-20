# Database Migration Guide - ML Stroke Guard

Folder ini berisi migration dan seed data untuk database **PostgreSQL di Neon**.

## Kebutuhan

- Database Neon aktif
- Connection string Neon di `.env`
- Virtual environment aktif

Contoh `.env` minimal:

```env
NEON_URL=postgresql://username:password@your-neon-host.neon.tech/neondb?sslmode=require
JWT_SECRET=replace-this-with-a-secure-random-value
```

Backend dan script migration juga tetap menerima `DATABASE_URL_DIRECT` atau `DATABASE_URL` sebagai alias, tapi `NEON_URL` sekarang jadi konfigurasi utama.

## Menjalankan migration

Dari folder root project:

```powershell
cd "e:\01_KULIAH\SEMESTER 5\Pengembangan Aplikasi Medis\Project-Akhir\ml-stroke-guard"
.\.venv\Scripts\Activate.ps1
python database\run_migration.py
```

Script akan:
- Menjalankan semua file di `database/migrations`
- Menjalankan seed admin user
- Menawarkan seed sample data opsional
- Memverifikasi tabel, view, dan user admin

## Default admin

Setelah seed berhasil:

```text
Email: admin@strokeguard.com
Password: Admin123!
```

Ganti password itu setelah login pertama.

## File penting

- `database/migrations/*.sql`: schema dan perubahan database
- `database/seeds/*.sql`: seed admin dan sample data
- `database/run_migration.py`: runner migration untuk Neon
- `database/schema.sql`: referensi schema lengkap

## Troubleshooting

Jika koneksi gagal:

- Pastikan `NEON_URL` valid
- Pastikan URL mengandung `sslmode=require`
- Pastikan project Neon tidak suspended
- Pastikan firewall atau jaringan tidak memblokir koneksi PostgreSQL

Jika migration gagal karena object sudah ada:

- Jalankan ke database kosong, atau
- rollback manual object yang bentrok dulu
