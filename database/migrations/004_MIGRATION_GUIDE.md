# 🔄 Database Migration - Add ML Output Fields

**Migration File:** `004_add_ml_output_fields.sql`  
**Date:** 2025-12-22  
**Purpose:** Menambahkan fields untuk menyimpan output lengkap dari ML model

---

## 📋 **What's New**

### **New Fields in `stroke_screenings` Table:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `risk_factors` | `TEXT[]` | Array of identified risk factors | `["Hypertension", "High BMI"]` |
| `confidence` | `VARCHAR(20)` | Model confidence level | `"High"`, `"Medium"`, `"Low"` |
| `prediction` | `INTEGER` | Binary prediction result | `0` (Low Risk) or `1` (High Risk) |
| `threshold` | `DECIMAL(5,4)` | Optimal threshold used | `0.5000` |

---

## 🚀 **How to Run Migration**

### **Option 1: Via Supabase Dashboard (Recommended)**

1. Login ke Supabase Dashboard
2. Buka **SQL Editor**
3. Copy-paste isi file `database/migrations/004_add_ml_output_fields.sql`
4. Klik **Run**
5. Done! ✅

### **Option 2: Via psql CLI**

```bash
psql $DATABASE_URL_DIRECT -f database/migrations/004_add_ml_output_fields.sql
```

---

## ✅ **Verification**

Setelah migration, jalankan query ini untuk verify:

```sql
-- Check if columns exist
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'stroke_screenings'
AND column_name IN ('risk_factors', 'confidence', 'prediction', 'threshold')
ORDER BY column_name;
```

**Expected Result:**
```
column_name   | data_type | is_nullable
--------------+-----------+-------------
confidence    | character varying | YES
prediction    | integer   | YES
risk_factors  | ARRAY     | YES
threshold     | numeric   | YES
```

---

## 📊 **Example Data**

### **Before Migration:**
```json
{
  "id": "uuid",
  "stroke_probability": 0.1523,
  "risk_level": "Low"
}
```

### **After Migration:**
```json
{
  "id": "uuid",
  "stroke_probability": 0.1523,
  "risk_level": "Low",
  "risk_factors": ["High BMI"],
  "confidence": "High",
  "prediction": 0,
  "threshold": 0.5
}
```

---

## 🔍 **What Each Field Means**

### **1. `risk_factors` (TEXT[])**

Array berisi faktor-faktor risiko yang teridentifikasi:

**Possible values:**
- `"Hypertension"` - Tekanan darah tinggi
- `"Heart Disease"` - Penyakit jantung
- `"High BMI"` - BMI ≥ 25
- `"High Glucose Level"` - Glucose ≥ 200 mg/dL
- `"Advanced Age"` - Usia ≥ 65 tahun

**Example:**
```json
"risk_factors": ["Hypertension", "High BMI", "Advanced Age"]
```

---

### **2. `confidence` (VARCHAR)**

Tingkat kepercayaan model terhadap prediksi:

**Calculation:**
```python
confidence_margin = abs(probability - 0.5)

if confidence_margin > 0.3:
    confidence = "High"
elif confidence_margin > 0.15:
    confidence = "Medium"
else:
    confidence = "Low"
```

**Meaning:**
- **High**: Model sangat yakin dengan prediksi (probability jauh dari 0.5)
- **Medium**: Model cukup yakin
- **Low**: Model kurang yakin (probability mendekati 0.5)

**Example:**
- Probability 0.95 → Confidence: "High" (margin = 0.45)
- Probability 0.60 → Confidence: "Medium" (margin = 0.10)
- Probability 0.52 → Confidence: "Low" (margin = 0.02)

---

### **3. `prediction` (INTEGER)**

Binary classification result:

**Values:**
- `0` = Low Risk (probability < threshold)
- `1` = High Risk (probability ≥ threshold)

**Example:**
- Probability 0.35, Threshold 0.5 → Prediction: `0` (Low Risk)
- Probability 0.75, Threshold 0.5 → Prediction: `1` (High Risk)

---

### **4. `threshold` (DECIMAL)**

Optimal threshold yang digunakan untuk classification:

**Default:** `0.5000`

Threshold ini di-optimize saat training model untuk balance antara sensitivity dan specificity.

---

## 📱 **Frontend Integration**

### **Updated Response Example:**

```javascript
// POST /screening/predict
const response = await fetch('http://localhost:8000/screening/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    height_cm: 170,
    weight_kg: 85,
    hypertension: true,
    heart_disease: false,
    ever_married: true,
    work_type: 'Private',
    residence_type: 'Urban',
    avg_glucose_level: 120,
    smoking_status: 'never smoked'
  })
});

const result = await response.json();

console.log('Risk Level:', result.risk_level);           // "Medium"
console.log('Probability:', result.stroke_probability);  // 0.4523
console.log('Risk Factors:', result.risk_factors);       // ["High BMI"]
console.log('Confidence:', result.confidence);           // "High"
console.log('Prediction:', result.prediction);           // 0
console.log('Threshold:', result.threshold);             // 0.5
```

---

## 🎨 **UI Display Suggestions**

### **Risk Factors Display:**

```jsx
{result.risk_factors && result.risk_factors.length > 0 && (
  <div className="risk-factors">
    <h3>Faktor Risiko Teridentifikasi:</h3>
    <ul>
      {result.risk_factors.map((factor, index) => (
        <li key={index}>
          <span className="icon">⚠️</span>
          {factor}
        </li>
      ))}
    </ul>
  </div>
)}
```

### **Confidence Badge:**

```jsx
<div className={`confidence-badge ${result.confidence.toLowerCase()}`}>
  Confidence: {result.confidence}
  {result.confidence === 'High' && ' ✓'}
  {result.confidence === 'Medium' && ' ~'}
  {result.confidence === 'Low' && ' ?'}
</div>
```

### **Detailed Result Card:**

```jsx
<div className="result-card">
  <h2>Hasil Screening</h2>
  
  <div className="main-result">
    <span className={`risk-level ${result.risk_level.toLowerCase()}`}>
      {result.risk_level} Risk
    </span>
    <span className="probability">
      {(result.stroke_probability * 100).toFixed(1)}%
    </span>
  </div>
  
  <div className="details">
    <p>Model Confidence: <strong>{result.confidence}</strong></p>
    <p>Prediction: <strong>{result.prediction === 1 ? 'High Risk' : 'Low Risk'}</strong></p>
  </div>
  
  {result.risk_factors && result.risk_factors.length > 0 && (
    <div className="risk-factors">
      <h3>⚠️ Faktor Risiko:</h3>
      <ul>
        {result.risk_factors.map((factor, i) => (
          <li key={i}>{factor}</li>
        ))}
      </ul>
      <p className="advice">
        Konsultasikan dengan dokter mengenai faktor-faktor risiko di atas.
      </p>
    </div>
  )}
</div>
```

---

## 🔄 **Rollback (if needed)**

Jika perlu rollback migration:

```sql
-- Remove added columns
ALTER TABLE stroke_screenings
DROP COLUMN IF EXISTS risk_factors,
DROP COLUMN IF EXISTS confidence,
DROP COLUMN IF EXISTS prediction,
DROP COLUMN IF EXISTS threshold;
```

---

## ✅ **Testing**

### **Test Query:**

```sql
-- Insert test data
INSERT INTO stroke_screenings (
    user_id, age_at_screening, height_cm, weight_kg, bmi,
    hypertension, heart_disease, ever_married, work_type,
    residence_type, avg_glucose_level, smoking_status,
    stroke_probability, risk_level,
    risk_factors, confidence, prediction, threshold
)
VALUES (
    'test-user-id', 35, 170, 85, 29.4,
    true, false, true, 'Private',
    'Urban', 120, 'never smoked',
    0.4523, 'Medium',
    ARRAY['High BMI'], 'High', 0, 0.5
)
RETURNING *;
```

---

## 📝 **Summary**

✅ **Added 4 new fields** to `stroke_screenings` table  
✅ **Backward compatible** - existing data not affected  
✅ **Frontend gets more detailed** prediction results  
✅ **Better user experience** - show why risk is high/medium/low  

---

**Migration Status:** ✅ Ready to Deploy  
**Breaking Changes:** ❌ None  
**Requires Frontend Update:** ✅ Yes (optional, to display new fields)

---

**Next Steps:**
1. Run migration via Supabase Dashboard
2. Restart backend server
3. Test screening endpoint
4. Update frontend to display new fields
