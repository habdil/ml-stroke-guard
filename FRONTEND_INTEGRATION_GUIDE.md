# 📱 StrokeGuard API - Frontend Integration Guide

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (development)  
**Last Updated:** 2025-12-22

---

## 🚀 Quick Start

### **1. Base Configuration**

```javascript
// config/api.js
const API_BASE_URL = 'http://localhost:8000';

const api = {
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  
  // Add auth token to headers
  setAuthToken: (token) => {
    if (token) {
      api.headers['Authorization'] = `Bearer ${token}`;
    } else {
      delete api.headers['Authorization'];
    }
  }
};

export default api;
```

---

## 🔐 Authentication Flow

### **Step 1: Register New User**

**Endpoint:** `POST /auth/register`

```javascript
// Example: Register
async function register(userData) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: "patient@example.com",
      password: "SecurePassword123!",
      full_name: "John Doe",
      date_of_birth: "1990-05-15",        // Format: YYYY-MM-DD
      gender: "Male",                      // "Male" or "Female"
      phone_number: "+6281234567890"       // Optional, must start with +
    })
  });
  
  const data = await response.json();
  return data;
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "patient@example.com",
  "full_name": "John Doe",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "phone_number": "+6281234567890",
  "role": "PATIENT",
  "created_at": "2025-12-22T14:00:00Z"
}
```

---

### **Step 2: Login**

**Endpoint:** `POST /auth/login`

```javascript
// Example: Login
async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Save token to localStorage
  localStorage.setItem('access_token', data.access_token);
  
  return data;
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**⚠️ Important:** Save `access_token` to localStorage/sessionStorage!

---

### **Step 3: Get Current User**

**Endpoint:** `GET /auth/me`

```javascript
// Example: Get current user
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

---

## 🩺 Screening (Main Feature)

### **Create Screening**

**Endpoint:** `POST /screening/predict`

**⚠️ Important Notes:**
- ✅ **Send height & weight** (NOT BMI) - backend will calculate BMI
- ✅ **DON'T send age** - backend calculates from user's date_of_birth
- ✅ **Requires authentication** - include Bearer token

```javascript
// Example: Create screening
async function createScreening(screeningData) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/screening/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      height_cm: 170.0,                    // User's height in cm
      weight_kg: 70.0,                     // User's weight in kg
      hypertension: false,                 // boolean
      heart_disease: false,                // boolean
      ever_married: true,                  // boolean
      work_type: "Private",                // See options below
      residence_type: "Urban",             // "Urban" or "Rural"
      avg_glucose_level: 95.5,             // mg/dL
      smoking_status: "never smoked"       // See options below
    })
  });
  
  return await response.json();
}
```

**Field Options:**

**`work_type`:** (choose one)
- `"Private"`
- `"Self-employed"`
- `"Govt_job"`
- `"children"`
- `"Never_worked"`

**`residence_type`:** (choose one)
- `"Urban"`
- `"Rural"`

**`smoking_status`:** (choose one)
- `"never smoked"`
- `"formerly smoked"`
- `"smokes"`
- `"Unknown"`

**Response:**
```json
{
  "id": "screening-uuid",
  "user_id": "user-uuid",
  "age_at_screening": 35,              // ← Calculated automatically
  "height_cm": 170.0,
  "weight_kg": 70.0,
  "bmi": 24.2,                         // ← Calculated automatically
  "hypertension": false,
  "heart_disease": false,
  "ever_married": true,
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 95.5,
  "smoking_status": "never smoked",
  "stroke_probability": 0.0523,        // ← ML prediction (0-1)
  "risk_level": "Low",                 // ← "Low", "Medium", or "High"
  "created_at": "2025-12-22T14:00:45Z"
}
```

**Risk Level Interpretation:**
- `"Low"`: probability < 0.4 (< 40%)
- `"Medium"`: 0.4 ≤ probability < 0.7 (40-70%)
- `"High"`: probability ≥ 0.7 (≥ 70%)

---

### **Get Screening History**

**Endpoint:** `GET /screening/history`

```javascript
// Example: Get history
async function getScreeningHistory() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/screening/history`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

**Response:**
```json
[
  {
    "id": "screening-uuid-1",
    "age_at_screening": 35,
    "bmi": 24.2,
    "risk_level": "Low",
    "stroke_probability": 0.0523,
    "created_at": "2025-12-22T14:00:45Z"
  },
  {
    "id": "screening-uuid-2",
    "age_at_screening": 35,
    "bmi": 25.0,
    "risk_level": "Medium",
    "stroke_probability": 0.4521,
    "created_at": "2025-12-20T10:30:00Z"
  }
]
```

---

### **Get Screening Detail**

**Endpoint:** `GET /screening/{screening_id}`

```javascript
// Example: Get detail
async function getScreeningDetail(screeningId) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(
    `${API_BASE_URL}/screening/${screeningId}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return await response.json();
}
```

---

## 👨‍⚕️ Admin Endpoints

**⚠️ Only accessible with ADMIN role!**

### **Get All Patients**

**Endpoint:** `GET /admin/patients`

```javascript
async function getAllPatients() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/admin/patients`, {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return await response.json();
}
```

**Response:**
```json
[
  {
    "id": "patient-uuid",
    "full_name": "John Doe",
    "email": "patient@example.com",
    "date_of_birth": "1990-05-15",
    "gender": "Male",
    "total_screenings": 2,
    "last_screening_date": "2025-12-22T14:00:45Z",
    "highest_risk_level": "Medium"
  }
]
```

---

### **Get Statistics**

**Endpoint:** `GET /admin/statistics`

```javascript
async function getStatistics() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/admin/statistics`, {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return await response.json();
}
```

---

### **Get Dashboard Stats**

**Endpoint:** `GET /admin/dashboard-stats`

```javascript
async function getDashboardStats() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}/admin/dashboard-stats`, {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return await response.json();
}
```

**Response:**
```json
{
  "total_patients": 150,
  "total_screenings": 523,
  "high_risk_count": 45,
  "recent_screenings_7days": 23
}
```

---

## ⚠️ Error Handling

### **Common Error Responses:**

**401 Unauthorized** - Token invalid/expired
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden** - Insufficient permissions
```json
{
  "detail": "Only admins can access this endpoint"
}
```

**400 Bad Request** - Validation error
```json
{
  "detail": "Email already registered"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Screening failed: <error message>"
}
```

### **Error Handling Example:**

```javascript
async function createScreeningWithErrorHandling(data) {
  try {
    const response = await fetch(`${API_BASE_URL}/screening/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      if (response.status === 401) {
        // Token expired - redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return;
      }
      
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Screening error:', error);
    throw error;
  }
}
```

---

## 🔄 Complete Integration Example

```javascript
// services/api.js
class StrokeGuardAPI {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }
  
  // Helper method
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  }
  
  // Auth
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }
  
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    localStorage.setItem('access_token', data.access_token);
    return data;
  }
  
  async getCurrentUser() {
    return this.request('/auth/me');
  }
  
  // Screening
  async createScreening(screeningData) {
    return this.request('/screening/predict', {
      method: 'POST',
      body: JSON.stringify(screeningData),
    });
  }
  
  async getHistory() {
    return this.request('/screening/history');
  }
  
  async getScreeningDetail(id) {
    return this.request(`/screening/${id}`);
  }
  
  // Admin
  async getAllPatients() {
    return this.request('/admin/patients');
  }
  
  async getStatistics() {
    return this.request('/admin/statistics');
  }
  
  async getDashboardStats() {
    return this.request('/admin/dashboard-stats');
  }
}

export default new StrokeGuardAPI();
```

**Usage:**
```javascript
import api from './services/api';

// Register
await api.register({
  email: "user@example.com",
  password: "Password123!",
  full_name: "John Doe",
  date_of_birth: "1990-05-15",
  gender: "Male",
  phone_number: "+6281234567890"
});

// Login
await api.login("user@example.com", "Password123!");

// Create screening
const result = await api.createScreening({
  height_cm: 170,
  weight_kg: 70,
  hypertension: false,
  heart_disease: false,
  ever_married: true,
  work_type: "Private",
  residence_type: "Urban",
  avg_glucose_level: 95.5,
  smoking_status: "never smoked"
});

console.log('Risk Level:', result.risk_level);
console.log('Probability:', result.stroke_probability);
```

---

## 📋 Checklist for Frontend Integration

- [ ] Setup API base URL configuration
- [ ] Implement authentication flow (register, login)
- [ ] Store JWT token in localStorage
- [ ] Add Authorization header to authenticated requests
- [ ] Create screening form with correct field types
- [ ] Handle screening response (show risk level & probability)
- [ ] Display screening history
- [ ] Implement error handling (401, 403, 400, 500)
- [ ] Add token expiry handling (redirect to login)
- [ ] Test all endpoints

---

## 🎯 Key Points to Remember

1. **DON'T send:**
   - ❌ `age` (calculated from date_of_birth)
   - ❌ `bmi` (calculated from height & weight)

2. **DO send:**
   - ✅ `height_cm` and `weight_kg`
   - ✅ All other fields as shown in examples

3. **Authentication:**
   - ✅ Always include `Bearer ${token}` in Authorization header
   - ✅ Handle 401 errors (token expired)

4. **Field Validation:**
   - Email must be valid format
   - Password minimum 8 characters
   - Phone number must start with `+`
   - Date format: `YYYY-MM-DD`

---

## 📞 Support

**API Documentation:** http://localhost:8000/docs  
**Interactive Testing:** http://localhost:8000/docs (Swagger UI)

---

**Happy Coding! 🚀**
