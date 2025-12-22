# 🚀 StrokeGuard API - Complete Documentation

## ✅ Setup Complete!

Backend Anda sekarang sudah **fully integrated** dengan database! 🎉

---

## 📁 Project Structure

```
ml-stroke-guard/
├── main.py                    # Main FastAPI app (UPDATED)
├── app/
│   ├── __init__.py
│   ├── database.py            # Database connection pool
│   ├── models.py              # Pydantic models
│   ├── auth.py                # JWT & password hashing
│   ├── dependencies.py        # Auth dependencies
│   └── routers/
│       ├── __init__.py
│       ├── auth.py            # /auth endpoints
│       ├── screening.py       # /screening endpoints
│       └── admin.py           # /admin endpoints
├── database/
│   └── ... (migration files)
├── ml/
│   └── ... (ML model)
└── requirements.txt           # (UPDATED)
```

---

## 🔧 Installation & Setup

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

**New dependencies added:**
- `psycopg2-binary` - PostgreSQL adapter
- `python-dotenv` - Environment variables
- `python-jose` - JWT tokens
- `passlib` - Password hashing
- `bcrypt` - Encryption

### **2. Configure Environment Variables**

Pastikan `.env` Anda sudah lengkap:

```env
# Database (sudah ada)
DATABASE_URL_DIRECT=postgresql://postgres:54qjvGR9jClGN6l0@db.ujwqvweresyqvdmjidlr.supabase.co:5432/postgres

# JWT Secret (tambahkan jika belum ada)
JWT_SECRET=your-super-secret-key-change-this-in-production-min-32-chars
```

**Generate JWT Secret yang aman:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### **3. Run the Server**

```bash
python main.py
```

atau

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: **http://localhost:8000**

---

## 📚 API Endpoints

### **Base URL:** `http://localhost:8000`

### **Interactive Docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔐 Authentication Endpoints

### **1. Register (Pasien Baru)**

**POST** `/auth/register`

**Request Body:**
```json
{
  "email": "patient@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "phone_number": "+6281234567890"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid-here",
  "email": "patient@example.com",
  "full_name": "John Doe",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "phone_number": "+6281234567890",
  "role": "PATIENT",
  "created_at": "2025-12-22T20:00:00Z"
}
```

---

### **2. Login**

**POST** `/auth/login`

**Request Body:**
```json
{
  "email": "patient@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Simpan `access_token` ini!** Gunakan untuk semua request yang memerlukan authentication.

---

### **3. Get Current User**

**GET** `/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid-here",
  "email": "patient@example.com",
  "full_name": "John Doe",
  ...
}
```

---

## 🩺 Screening Endpoints (Pasien)

**⚠️ Semua endpoint ini memerlukan authentication!**

### **1. Create Screening (Predict)**

**POST** `/screening/predict`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "height_cm": 170.0,
  "weight_kg": 70.0,
  "hypertension": false,
  "heart_disease": false,
  "ever_married": true,
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 95.5,
  "smoking_status": "never smoked"
}
```

**Response:** `201 Created`
```json
{
  "id": "screening-uuid",
  "user_id": "user-uuid",
  "age_at_screening": 35,
  "height_cm": 170.0,
  "weight_kg": 70.0,
  "bmi": 24.2,
  "hypertension": false,
  "heart_disease": false,
  "ever_married": true,
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 95.5,
  "smoking_status": "never smoked",
  "stroke_probability": 0.1523,
  "risk_level": "Low",
  "created_at": "2025-12-22T20:00:00Z"
}
```

**✨ What happens:**
1. Age dihitung otomatis dari `date_of_birth` user
2. BMI dihitung otomatis dari `height_cm` & `weight_kg`
3. Data dikirim ke ML model
4. Hasil prediction disimpan ke database
5. Return hasil lengkap

---

### **2. Get Screening History**

**GET** `/screening/history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "screening-uuid-1",
    "age_at_screening": 35,
    "bmi": 24.2,
    "risk_level": "Low",
    "stroke_probability": 0.1523,
    "created_at": "2025-12-22T20:00:00Z"
  },
  {
    "id": "screening-uuid-2",
    "age_at_screening": 35,
    "bmi": 25.0,
    "risk_level": "Medium",
    "stroke_probability": 0.4521,
    "created_at": "2025-12-20T15:30:00Z"
  }
]
```

---

### **3. Get Screening Detail**

**GET** `/screening/{screening_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "screening-uuid",
  "user_id": "user-uuid",
  "age_at_screening": 35,
  "height_cm": 170.0,
  "weight_kg": 70.0,
  "bmi": 24.2,
  ...
  "stroke_probability": 0.1523,
  "risk_level": "Low",
  "created_at": "2025-12-22T20:00:00Z"
}
```

---

## 👨‍⚕️ Admin Endpoints

**⚠️ Hanya accessible oleh user dengan role ADMIN!**

### **Admin Login:**
```json
{
  "email": "admin@strokeguard.com",
  "password": "Admin123!"
}
```

---

### **1. Get All Patients**

**GET** `/admin/patients`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "patient-uuid-1",
    "full_name": "John Doe",
    "email": "john@example.com",
    "date_of_birth": "1990-05-15",
    "gender": "Male",
    "total_screenings": 3,
    "last_screening_date": "2025-12-22T20:00:00Z",
    "highest_risk_level": "Medium"
  },
  ...
]
```

---

### **2. Get Statistics**

**GET** `/admin/statistics`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:** `200 OK`
```json
[
  {
    "risk_level": "High",
    "total_count": 5,
    "avg_age": 52.4,
    "avg_bmi": 28.3,
    "avg_glucose": 145.2,
    "avg_probability": 0.7823,
    "hypertension_count": 4,
    "heart_disease_count": 3
  },
  {
    "risk_level": "Medium",
    ...
  },
  {
    "risk_level": "Low",
    ...
  }
]
```

---

### **3. Get High-Risk Screenings (Last 30 Days)**

**GET** `/admin/high-risk-screenings`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "screening-uuid",
    "user_id": "patient-uuid",
    "full_name": "Jane Smith",
    "email": "jane@example.com",
    "phone_number": "+6281234567890",
    "age_at_screening": 55,
    "bmi": 32.1,
    "stroke_probability": 0.8521,
    "risk_level": "High",
    "created_at": "2025-12-20T10:30:00Z"
  },
  ...
]
```

---

### **4. Get Patient's Screenings**

**GET** `/admin/patient/{patient_id}/screenings`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "screening-uuid-1",
    "user_id": "patient-uuid",
    "age_at_screening": 35,
    "height_cm": 170.0,
    ...
    "stroke_probability": 0.1523,
    "risk_level": "Low",
    "created_at": "2025-12-22T20:00:00Z"
  },
  ...
]
```

---

### **5. Get Dashboard Stats**

**GET** `/admin/dashboard-stats`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:** `200 OK`
```json
{
  "total_patients": 150,
  "total_screenings": 523,
  "high_risk_count": 45,
  "recent_screenings_7days": 23
}
```

---

## 🔒 Authentication Flow

### **Frontend Integration:**

```javascript
// 1. Register
const registerResponse = await fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'patient@example.com',
    password: 'SecurePassword123!',
    full_name: 'John Doe',
    date_of_birth: '1990-05-15',
    gender: 'Male',
    phone_number: '+6281234567890'
  })
});

// 2. Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'patient@example.com',
    password: 'SecurePassword123!'
  })
});

const { access_token } = await loginResponse.json();

// 3. Simpan token (localStorage, sessionStorage, atau state management)
localStorage.setItem('access_token', access_token);

// 4. Use token untuk authenticated requests
const screeningResponse = await fetch('http://localhost:8000/screening/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    height_cm: 170,
    weight_kg: 70,
    hypertension: false,
    heart_disease: false,
    ever_married: true,
    work_type: 'Private',
    residence_type: 'Urban',
    avg_glucose_level: 95.5,
    smoking_status: 'never smoked'
  })
});

const result = await screeningResponse.json();
console.log('Screening result:', result);
```

---

## 🧪 Testing dengan cURL

### **Register:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456!",
    "full_name": "Test User",
    "date_of_birth": "1995-01-01",
    "gender": "Male",
    "phone_number": "+6281234567890"
  }'
```

### **Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456!"
  }'
```

### **Screening:**
```bash
curl -X POST http://localhost:8000/screening/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "height_cm": 170,
    "weight_kg": 70,
    "hypertension": false,
    "heart_disease": false,
    "ever_married": true,
    "work_type": "Private",
    "residence_type": "Urban",
    "avg_glucose_level": 95.5,
    "smoking_status": "never smoked"
  }'
```

---

## 🎯 Next Steps

1. ✅ **Test API** - Gunakan Swagger UI di `/docs`
2. ✅ **Update Frontend** - Integrate dengan endpoints baru
3. ✅ **Security** - Ganti JWT_SECRET di production
4. ✅ **Deployment** - Deploy ke server

---

## 🐛 Troubleshooting

### **Error: "Failed to initialize database"**
- Cek `DATABASE_URL_DIRECT` di `.env`
- Pastikan Supabase database accessible

### **Error: "Invalid authentication credentials"**
- Token expired (default 24 jam)
- Login ulang untuk dapat token baru

### **Error: "Only patients can access this endpoint"**
- Endpoint hanya untuk PATIENT role
- Pastikan login sebagai patient, bukan admin

### **Error: "Only admins can access this endpoint"**
- Endpoint hanya untuk ADMIN role
- Login dengan `admin@strokeguard.com`

---

**Selamat! Backend Anda sudah fully integrated! 🚀**
