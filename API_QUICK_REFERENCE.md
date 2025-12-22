# 📋 API Quick Reference Card

**Base URL:** `http://localhost:8000`

---

## 🔐 Authentication

| Endpoint | Method | Auth | Body |
|----------|--------|------|------|
| `/auth/register` | POST | ❌ | `{ email, password, full_name, date_of_birth, gender, phone_number? }` |
| `/auth/login` | POST | ❌ | `{ email, password }` |
| `/auth/me` | GET | ✅ | - |

---

## 🩺 Screening

| Endpoint | Method | Auth | Body |
|----------|--------|------|------|
| `/screening/predict` | POST | ✅ | `{ height_cm, weight_kg, hypertension, heart_disease, ever_married, work_type, residence_type, avg_glucose_level, smoking_status }` |
| `/screening/history` | GET | ✅ | - |
| `/screening/{id}` | GET | ✅ | - |

---

## 👨‍⚕️ Admin (ADMIN only)

| Endpoint | Method | Auth | Body |
|----------|--------|------|------|
| `/admin/patients` | GET | ✅ | - |
| `/admin/statistics` | GET | ✅ | - |
| `/admin/dashboard-stats` | GET | ✅ | - |
| `/admin/patient/{id}/screenings` | GET | ✅ | - |
| `/admin/high-risk-screenings` | GET | ✅ | - |

---

## 📝 Field Options

**`gender`:** `"Male"` | `"Female"`

**`work_type`:**
- `"Private"`
- `"Self-employed"`
- `"Govt_job"`
- `"children"`
- `"Never_worked"`

**`residence_type`:** `"Urban"` | `"Rural"`

**`smoking_status`:**
- `"never smoked"`
- `"formerly smoked"`
- `"smokes"`
- `"Unknown"`

---

## 🔑 Headers

**All requests:**
```javascript
{
  'Content-Type': 'application/json'
}
```

**Authenticated requests:**
```javascript
{
  'Content-Type': 'application/json',
  'Authorization': 'Bearer YOUR_TOKEN_HERE'
}
```

---

## ⚠️ Important Notes

1. **DON'T send `age`** - Backend calculates from `date_of_birth`
2. **DON'T send `bmi`** - Backend calculates from `height_cm` & `weight_kg`
3. **DO save token** - Store `access_token` from login response
4. **Token expires** - After 24 hours, need to login again

---

## 🎯 Quick Example

```javascript
// 1. Login
const loginRes = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123!'
  })
});
const { access_token } = await loginRes.json();

// 2. Create Screening
const screeningRes = await fetch('http://localhost:8000/screening/predict', {
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
const result = await screeningRes.json();

console.log('Risk:', result.risk_level);        // "Low", "Medium", or "High"
console.log('Probability:', result.stroke_probability); // 0.0 - 1.0
```

---

## 📚 Full Documentation

See `FRONTEND_INTEGRATION_GUIDE.md` for complete examples and error handling.

---

**API Docs:** http://localhost:8000/docs
