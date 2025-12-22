"""
Screening router (predict & save to database)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models import ScreeningInput, ScreeningResponse, ScreeningSummary
from app.dependencies import get_current_patient
from app.database import get_db_cursor
from ml.utils.prediction import StrokePredictor
from datetime import date
import logging

router = APIRouter(prefix="/screening", tags=["Screening"])
logger = logging.getLogger(__name__)

# Initialize ML predictor
try:
    predictor = StrokePredictor()
    logger.info("ML Model loaded successfully in screening router")
except Exception as e:
    logger.error(f"Failed to load ML model: {e}")
    predictor = None

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI"""
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

def get_risk_level(probability: float) -> str:
    """Determine risk level from probability"""
    if probability >= 0.7:
        return "High"
    elif probability >= 0.4:
        return "Medium"
    else:
        return "Low"

def prepare_ml_input(screening_data: dict, age: int, bmi: float) -> dict:
    """
    Prepare input for ML model
    Convert from user-friendly format to ML model format
    """
    # Gender mapping
    gender_map = {"Male": 1, "Female": 0}
    
    # Work type one-hot encoding
    work_type_encoding = {
        "Govt_job": [1, 0, 0, 0, 0],
        "Never_worked": [0, 1, 0, 0, 0],
        "Private": [0, 0, 1, 0, 0],
        "Self-employed": [0, 0, 0, 1, 0],
        "children": [0, 0, 0, 0, 1]
    }
    
    # Smoking status one-hot encoding
    smoking_encoding = {
        "Unknown": [1, 0, 0, 0],
        "formerly smoked": [0, 1, 0, 0],
        "never smoked": [0, 0, 1, 0],
        "smokes": [0, 0, 0, 1]
    }
    
    # Residence type mapping
    residence_map = {"Urban": 1, "Rural": 0}
    
    work_type = screening_data["work_type"]
    smoking_status = screening_data["smoking_status"]
    
    work_encoding = work_type_encoding.get(work_type, [0, 0, 1, 0, 0])  # Default to Private
    smoking_enc = smoking_encoding.get(smoking_status, [0, 0, 1, 0])  # Default to never smoked
    
    return {
        "age": age,
        "gender": gender_map.get(screening_data.get("gender", "Male"), 1),
        "hypertension": int(screening_data["hypertension"]),
        "heart_disease": int(screening_data["heart_disease"]),
        "ever_married": int(screening_data["ever_married"]),
        "Residence_type": residence_map.get(screening_data["residence_type"], 1),
        "avg_glucose_level": screening_data["avg_glucose_level"],
        "bmi": bmi,
        "work_type_Govt_job": work_encoding[0],
        "work_type_Never_worked": work_encoding[1],
        "work_type_Private": work_encoding[2],
        "work_type_Self_employed": work_encoding[3],
        "work_type_children": work_encoding[4],
        "smoking_status_Unknown": smoking_enc[0],
        "smoking_status_formerly_smoked": smoking_enc[1],
        "smoking_status_never_smoked": smoking_enc[2],
        "smoking_status_smokes": smoking_enc[3]
    }

@router.post("/predict", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
async def create_screening(
    screening: ScreeningInput,
    current_user: dict = Depends(get_current_patient)
):
    """
    Perform stroke screening and save to database
    Only accessible by authenticated patients
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not available"
        )
    
    try:
        # Calculate age from user's date_of_birth
        age = calculate_age(current_user["date_of_birth"])
        
        # Calculate BMI
        bmi = calculate_bmi(screening.height_cm, screening.weight_kg)
        
        # Prepare input for ML model
        ml_input = prepare_ml_input(
            {
                "gender": current_user["gender"],
                "hypertension": screening.hypertension,
                "heart_disease": screening.heart_disease,
                "ever_married": screening.ever_married,
                "work_type": screening.work_type.value,
                "residence_type": screening.residence_type.value,
                "avg_glucose_level": screening.avg_glucose_level,
                "smoking_status": screening.smoking_status.value
            },
            age,
            bmi
        )
        
        # Make prediction
        prediction_result = predictor.make_prediction(ml_input)
        
        # Extract all ML model outputs
        stroke_probability = prediction_result.get("probability", 0.0)
        risk_factors = prediction_result.get("risk_factors", [])
        confidence = prediction_result.get("confidence", "Medium")
        prediction = prediction_result.get("prediction", 0)
        threshold = prediction_result.get("threshold", 0.5)
        risk_level = get_risk_level(stroke_probability)
        
        logger.info(f"Prediction made for user {current_user['email']}: {risk_level} ({stroke_probability:.4f})")
        logger.info(f"Risk factors: {risk_factors}, Confidence: {confidence}")
        
        # Save to database
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO stroke_screenings (
                    user_id, age_at_screening, height_cm, weight_kg, bmi,
                    hypertension, heart_disease, ever_married, work_type,
                    residence_type, avg_glucose_level, smoking_status,
                    stroke_probability, risk_level,
                    risk_factors, confidence, prediction, threshold
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, age_at_screening, height_cm, weight_kg, bmi,
                          hypertension, heart_disease, ever_married, work_type,
                          residence_type, avg_glucose_level, smoking_status,
                          stroke_probability, risk_level,
                          risk_factors, confidence, prediction, threshold, created_at
                """,
                (
                    current_user["id"],
                    age,
                    screening.height_cm,
                    screening.weight_kg,
                    bmi,
                    screening.hypertension,
                    screening.heart_disease,
                    screening.ever_married,
                    screening.work_type.value,
                    screening.residence_type.value,
                    screening.avg_glucose_level,
                    screening.smoking_status.value,
                    stroke_probability,
                    risk_level,
                    risk_factors,  # Array of risk factors
                    confidence,    # Confidence level
                    prediction,    # Binary prediction
                    threshold      # Threshold used
                )
            )
            
            result = cursor.fetchone()
            logger.info(f"Screening saved to database with ID: {result['id']}")
            
            return ScreeningResponse(**dict(result))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screening error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screening failed: {str(e)}"
        )

@router.get("/history", response_model=List[ScreeningSummary])
async def get_screening_history(
    current_user: dict = Depends(get_current_patient)
):
    """
    Get screening history for current patient
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, age_at_screening, bmi, risk_level, 
                       stroke_probability, created_at
                FROM stroke_screenings
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (current_user["id"],)
            )
            
            screenings = cursor.fetchall()
            return [ScreeningSummary(**dict(s)) for s in screenings]
            
    except Exception as e:
        logger.error(f"Error fetching screening history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch screening history"
        )

@router.get("/{screening_id}", response_model=ScreeningResponse)
async def get_screening_detail(
    screening_id: str,
    current_user: dict = Depends(get_current_patient)
):
    """
    Get detailed screening result by ID
    Only accessible by the patient who owns the screening
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, age_at_screening, height_cm, weight_kg, bmi,
                       hypertension, heart_disease, ever_married, work_type,
                       residence_type, avg_glucose_level, smoking_status,
                       stroke_probability, risk_level,
                       risk_factors, confidence, prediction, threshold, created_at
                FROM stroke_screenings
                WHERE id = %s AND user_id = %s
                """,
                (screening_id, current_user["id"])
            )
            
            screening = cursor.fetchone()
            
            if not screening:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Screening not found"
                )
            
            return ScreeningResponse(**dict(screening))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching screening detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch screening detail"
        )
