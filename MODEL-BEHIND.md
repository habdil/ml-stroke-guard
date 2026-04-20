# Model Behind StrokeGuard: Random Forest Classifier

## Overview
StrokeGuard menggunakan **Random Forest Classifier** untuk memprediksi risiko stroke berdasarkan data kesehatan pasien.

---

## Architecture Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT DATA PASIEN                            │
│  Age | BMI | Glucose | Hypertension | Heart Disease | Gender   │
│  50  | 29.4|   150   |      Yes     |      No       | Male     │
│  + Work Type + Residence + Smoking Status + Ever Married        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Data Preprocessing]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              RANDOM FOREST MODEL (100+ Trees)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Tree #1        Tree #2        Tree #3    ...    Tree #100    │
│     ┌─┐            ┌─┐            ┌─┐              ┌─┐         │
│     │?│            │?│            │?│              │?│         │
│    ┌┴─┴┐          ┌┴─┴┐          ┌┴─┴┐            ┌┴─┴┐        │
│   ┌┘   └┐        ┌┘   └┐        ┌┘   └┐          ┌┘   └┐       │
│   0     1        0     1        1     1          0     1       │
│   ↓     ↓        ↓     ↓        ↓     ↓          ↓     ↓       │
│  No   Stroke    No   Stroke  Stroke Stroke     No   Stroke    │
│                                                                 │
│  Vote: 0.4      Vote: 0.6     Vote: 0.7    ...  Vote: 0.5     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                      [Averaging Votes]
                              ↓
                    ┌──────────────────┐
                    │ Probability = 52%│
                    └──────────────────┘
                              ↓
                    [Risk Level Mapping]
                              ↓
           ┌──────────────────────────────────┐
           │  < 40%  →  Low Risk       🟢    │
           │  40-55% →  Medium Risk    🟡    │
           │  ≥ 56%  →  High Risk      🔴    │
           └──────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  MEDIUM RISK     │
                    │  Probability: 52%│
                    └──────────────────┘
```

---

## How It Works (Step by Step)

### 1️⃣ **Input Processing**
```
Patient Data (Raw) → Preprocessed Features
──────────────────────────────────────────
Age: 50 years       → age: 50
Height: 170 cm      → bmi: 29.4 (calculated)
Weight: 85 kg
Hypertension: Yes   → hypertension: 1
Work: Self-employed → work_type_Self-employed: 1
                      work_type_Private: 0
                      work_type_Govt_job: 0
                      ... (one-hot encoding)
```

### 2️⃣ **Random Forest Prediction**
```
┌────────────────────────────────┐
│  Each tree makes a decision:   │
├────────────────────────────────┤
│  Tree 1:  "Stroke" (prob: 0.6) │
│  Tree 2:  "No Stroke" (0.3)    │
│  Tree 3:  "Stroke" (0.8)       │
│  ...                           │
│  Tree 100: "Stroke" (0.5)      │
└────────────────────────────────┘
         ↓
    Average all votes
         ↓
  Final Probability: 0.52 (52%)
```

**Formula:**
```
Probability = (Sum of all tree votes) / (Total number of trees)
            = (0.6 + 0.3 + 0.8 + ... + 0.5) / 100
            = 0.52
```

### 3️⃣ **Risk Factors Detection**
```python
# Rule-based analysis
if hypertension == True:          → ✓ "Hypertension"
if heart_disease == True:         → ✗ (No)
if bmi >= 25:                     → ✓ "High BMI"
if avg_glucose_level >= 200:     → ✗ (150 < 200)
if age >= 65:                     → ✗ (50 < 65)

Result: ["Hypertension", "High BMI"]
```

### 4️⃣ **Confidence Calculation**
```
Distance from threshold (50%):
│
│         Low Confidence Zone
│    ◄────────────────────►
│    |                    |
│    35%   45%  50%  55%  65%
│            ├────┤
│            You are here (52%)
│
confidence_margin = |52% - 50%| = 2%

If margin > 30%  → High Confidence
If margin > 15%  → Medium Confidence
Else             → Low Confidence ✓
```

### 5️⃣ **Risk Level Mapping**
```
Probability: 52%
     ↓
┌─────────────────────────┐
│  Is prob ≥ 56%?  NO    │
│  Is prob ≥ 40%?  YES ✓ │
│  Else: Low             │
└─────────────────────────┘
     ↓
Risk Level: MEDIUM
```

---

## Why Random Forest?

### ✅ Advantages

1. **High Accuracy**
   - Combines multiple trees → reduces overfitting
   - More robust than single decision tree

2. **Handles Complex Patterns**
   ```
   Single Tree:          Random Forest:

   Age > 60? Yes        Tree 1: Age > 60
      ↓                 Tree 2: BMI > 25 AND Glucose > 150
   High Risk           Tree 3: Hypertension OR Heart Disease
                       → Combined = Better predictions
   ```

3. **Feature Importance**
   - Identifies which factors matter most
   - Example: Age might be 30% important, BMI 20%, etc.

4. **Robust to Outliers**
   - Averaging reduces impact of anomalies

---

## Model Training Process (Simplified)

```
┌─────────────────┐
│ Dataset         │
│ 5000+ patients  │
│ (historical)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Split Data      │
│ • 80% Training  │
│ • 20% Testing   │
└────────┬────────┘
         │
         ↓
┌─────────────────────┐
│ Train RF Model      │
│ • Build 100 trees   │
│ • Learn patterns    │
│ • Optimize params   │
└────────┬────────────┘
         │
         ↓
┌─────────────────────┐
│ Validate & Test     │
│ • Check accuracy    │
│ • Tune threshold    │
└────────┬────────────┘
         │
         ↓
┌─────────────────────┐
│ Save Model          │
│ optimized_stroke_   │
│ model.joblib        │
└─────────────────────┘
```

---

## Key Metrics

| Metric | Value | Meaning |
|--------|-------|---------|
| **Accuracy** | ~85%+ | Correct predictions out of total |
| **Precision** | ~80%+ | True positives / (True + False positives) |
| **Recall** | ~75%+ | True positives / (True + False negatives) |
| **Optimal Threshold** | ~0.5 | Best cutoff for classification |

---

## Risk Level Thresholds

```
 0%                    40%      56%                   100%
  ├──────────────────────┼────────┼──────────────────────┤
  │       LOW RISK       │ MEDIUM │     HIGH RISK        │
  │        🟢           │   🟡   │        🔴            │
  └──────────────────────┴────────┴──────────────────────┘
```

**Decision Logic:**
```python
if probability >= 0.56:
    return "High"       # 🔴 Urgent attention needed
elif probability >= 0.40:
    return "Medium"     # 🟡 Monitor closely
else:
    return "Low"        # 🟢 Maintain healthy lifestyle
```

---

## Example Prediction

### Input:
```
Patient: Male, 50 years old
BMI: 29.4 (Overweight)
Glucose: 150 mg/dL
Hypertension: Yes
Heart Disease: No
Smoking: Formerly smoked
Work: Self-employed
```

### Process:
```
Step 1: Encode features → 18 numerical values
Step 2: Random Forest → 100 trees vote
Step 3: Average votes → Probability = 52%
Step 4: Detect risk factors → ["Hypertension", "High BMI"]
Step 5: Calculate confidence → Low (close to 50%)
Step 6: Map to risk level → Medium (40% ≤ 52% < 56%)
```

### Output:
```
Risk Level: MEDIUM 🟡
Probability: 52%
Risk Factors: Hypertension, High BMI
Confidence: Low
Recommendation: Regular monitoring, lifestyle changes
```

---

## Technical Stack

```
┌──────────────────────────────────┐
│   Frontend (User Input)          │
└────────────┬─────────────────────┘
             │
             ↓
┌──────────────────────────────────┐
│   FastAPI Backend                │
│   • Receive request              │
│   • Validate data                │
│   • Call ML model                │
└────────────┬─────────────────────┘
             │
             ↓
┌──────────────────────────────────┐
│   StrokePredictor Class          │
│   (ml/utils/prediction.py)       │
│   • Load model                   │
│   • Preprocess input             │
│   • Make prediction              │
└────────────┬─────────────────────┘
             │
             ↓
┌──────────────────────────────────┐
│   RandomForestClassifier         │
│   (scikit-learn)                 │
│   • 100+ decision trees          │
│   • Trained on historical data   │
└────────────┬─────────────────────┘
             │
             ↓
┌──────────────────────────────────┐
│   Result Processing              │
│   • Map probability to risk      │
│   • Calculate confidence         │
│   • Identify risk factors        │
└────────────┬─────────────────────┘
             │
             ↓
┌──────────────────────────────────┐
│   Save to Database               │
│   (PostgreSQL/Supabase)          │
└────────────┬─────────────────────┘
             │
             ↓
┌──────────────────────────────────┐
│   Return JSON Response           │
│   to Frontend                    │
└──────────────────────────────────┘
```

---

## Summary

**StrokeGuard** menggunakan **Random Forest** untuk:
1. ✅ Menerima data kesehatan pasien
2. ✅ Menggabungkan prediksi dari 100+ decision trees
3. ✅ Menghitung probabilitas stroke (0-100%)
4. ✅ Mengidentifikasi faktor risiko utama
5. ✅ Mengkategorikan ke Low/Medium/High risk
6. ✅ Memberikan confidence level
7. ✅ Menyimpan hasil untuk monitoring

**Akurat, Cepat, dan Mudah dipahami!** 🎯
