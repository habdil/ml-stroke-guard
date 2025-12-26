# Test Cases - StrokeGuard API

## Overview
Dokumen ini berisi test cases untuk menguji endpoint `/screening/predict` dengan berbagai skenario risiko stroke: **Low**, **Medium**, dan **High**.

---

## Risk Level Categories

| Risk Level | Probability Range | Description |
|-----------|-------------------|-------------|
| **Low** | < 0.40 (< 40%) | Risiko rendah stroke |
| **Medium** | 0.40 - 0.55 (40% - 55%) | Risiko sedang stroke |
| **High** | ≥ 0.56 (≥ 56%) | Risiko tinggi stroke |

---

## Test Case 1: LOW RISK

### User Profile
```json
{
  "email": "lowrisk@test.com",
  "password": "testpassword123",
  "full_name": "Low Risk Patient",
  "date_of_birth": "1995-06-15",
  "gender": "Female",
  "phone_number": "+628123456789"
}
```

### Screening Input
```json
{
  "height_cm": 165,
  "weight_kg": 60,
  "hypertension": false,
  "heart_disease": false,
  "ever_married": false,
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 90,
  "smoking_status": "never smoked"
}
```

### Expected Output
- **risk_level**: `"Low"`
- **stroke_probability**: < 0.40
- **risk_factors**: `[]` (empty - no major risk factors)
- **Calculated values**:
  - Age: ~30 years
  - BMI: ~22.0 (Normal weight)
  - No hypertension
  - No heart disease
  - Normal glucose level

---

## Test Case 2: MEDIUM RISK

### User Profile
```json
{
  "email": "mediumrisk@test.com",
  "password": "testpassword123",
  "full_name": "Medium Risk Patient",
  "date_of_birth": "1975-03-20",
  "gender": "Male",
  "phone_number": "+628234567890"
}
```

### Screening Input
```json
{
  "height_cm": 170,
  "weight_kg": 85,
  "hypertension": true,
  "heart_disease": false,
  "ever_married": true,
  "work_type": "Self-employed",
  "residence_type": "Rural",
  "avg_glucose_level": 150,
  "smoking_status": "formerly smoked"
}
```

### Expected Output
- **risk_level**: `"Medium"`
- **stroke_probability**: 0.40 - 0.55
- **risk_factors**: `["Hypertension", "High BMI"]`
- **Calculated values**:
  - Age: ~50 years
  - BMI: ~29.4 (Overweight)
  - Has hypertension
  - No heart disease
  - Elevated glucose level

---

## Test Case 3: HIGH RISK

### User Profile
```json
{
  "email": "highrisk@test.com",
  "password": "testpassword123",
  "full_name": "High Risk Patient",
  "date_of_birth": "1950-08-10",
  "gender": "Male",
  "phone_number": "+628345678901"
}
```

### Screening Input
```json
{
  "height_cm": 168,
  "weight_kg": 95,
  "hypertension": true,
  "heart_disease": true,
  "ever_married": true,
  "work_type": "Govt_job",
  "residence_type": "Urban",
  "avg_glucose_level": 220,
  "smoking_status": "smokes"
}
```

### Expected Output
- **risk_level**: `"High"`
- **stroke_probability**: ≥ 0.56
- **risk_factors**: `["Hypertension", "Heart Disease", "High BMI", "High Glucose Level", "Advanced Age"]`
- **Calculated values**:
  - Age: ~75 years (Advanced Age ≥ 65)
  - BMI: ~33.7 (Obese, ≥ 25)
  - Has hypertension
  - Has heart disease
  - High glucose level (≥ 200)

---

## Risk Factors Criteria

| Risk Factor | Condition |
|------------|-----------|
| Hypertension | `hypertension == true` |
| Heart Disease | `heart_disease == true` |
| High BMI | BMI ≥ 25 |
| High Glucose Level | `avg_glucose_level ≥ 200` |
| Advanced Age | Age ≥ 65 years |

---

## Testing Steps

### 1. Register Users
```bash
# Test Case 1: Low Risk
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "lowrisk@test.com",
  "password": "testpassword123",
  "full_name": "Low Risk Patient",
  "date_of_birth": "1995-06-15",
  "gender": "Female",
  "phone_number": "+628123456789"
}

# Test Case 2: Medium Risk
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "mediumrisk@test.com",
  "password": "testpassword123",
  "full_name": "Medium Risk Patient",
  "date_of_birth": "1975-03-20",
  "gender": "Male",
  "phone_number": "+628234567890"
}

# Test Case 3: High Risk
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "highrisk@test.com",
  "password": "testpassword123",
  "full_name": "High Risk Patient",
  "date_of_birth": "1950-08-10",
  "gender": "Male",
  "phone_number": "+628345678901"
}
```

### 2. Login and Get Token
```bash
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "lowrisk@test.com",
  "password": "testpassword123"
}

# Save the access_token from response
```

### 3. Perform Screening
```bash
POST http://localhost:8000/screening/predict
Content-Type: application/json
Authorization: Bearer <access_token>

# Use the screening input JSON from each test case above
```

### 4. Verify Results
Check the response for:
- Correct `risk_level` (Low/Medium/High)
- Appropriate `stroke_probability` range
- Correct `risk_factors` array
- Properly calculated `bmi`
- Proper `age_at_screening`

---

## Additional Edge Cases

### Test Case 4: Borderline Low-Medium (probability ≈ 0.40)
```json
{
  "height_cm": 165,
  "weight_kg": 70,
  "hypertension": true,
  "heart_disease": false,
  "ever_married": true,
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 120,
  "smoking_status": "never smoked"
}
```
**User**: 45 years old, Female

---

### Test Case 5: Borderline Medium-High (probability ≈ 0.56)
```json
{
  "height_cm": 170,
  "weight_kg": 90,
  "hypertension": true,
  "heart_disease": true,
  "ever_married": true,
  "work_type": "Self-employed",
  "residence_type": "Rural",
  "avg_glucose_level": 180,
  "smoking_status": "smokes"
}
```
**User**: 68 years old, Male

---

## Expected API Response Format

```json
{
  "id": "uuid-here",
  "user_id": "user-uuid-here",
  "age_at_screening": 30,
  "height_cm": 165.0,
  "weight_kg": 60.0,
  "bmi": 22.0,
  "hypertension": false,
  "heart_disease": false,
  "ever_married": false,
  "work_type": "Private",
  "residence_type": "Urban",
  "avg_glucose_level": 90.0,
  "smoking_status": "never smoked",
  "stroke_probability": 0.15,
  "risk_level": "Low",
  "created_at": "2025-12-26T12:00:00Z"
}
```

---

## Notes
- Probabilitas yang **exact** akan bergantung pada model ML yang sudah di-train
- Test cases ini dirancang untuk mencakup berbagai kombinasi risk factors
- Pastikan database sudah di-setup dengan benar sebelum testing
- Gunakan tools seperti **Postman**, **Thunder Client**, atau **curl** untuk testing
- Token JWT harus di-include di header Authorization untuk semua request screening

---

## Success Criteria
✅ Low risk case returns probability < 0.40
✅ Medium risk case returns probability 0.40 - 0.55
✅ High risk case returns probability ≥ 0.56
✅ Risk factors array correctly identifies all applicable factors
✅ BMI calculated correctly (weight_kg / (height_m)²)
✅ Age calculated correctly from date_of_birth
✅ Data saved to database successfully
