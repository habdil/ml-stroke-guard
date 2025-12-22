"""
Admin router (view patients, statistics)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models import PatientSummary, ScreeningStatistics, ScreeningResponse
from app.dependencies import get_current_admin
from app.database import get_db_cursor
import logging

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

@router.get("/patients", response_model=List[PatientSummary])
async def get_all_patients(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get all patients with screening summary
    Only accessible by admins
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM user_screening_summary
                ORDER BY last_screening_date DESC NULLS LAST
                """
            )
            
            patients = cursor.fetchall()
            return [PatientSummary(**dict(p)) for p in patients]
            
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patients"
        )

@router.get("/statistics", response_model=List[ScreeningStatistics])
async def get_screening_statistics(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get screening statistics by risk level
    Only accessible by admins
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM screening_statistics")
            
            stats = cursor.fetchall()
            return [ScreeningStatistics(**dict(s)) for s in stats]
            
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )

@router.get("/high-risk-screenings", response_model=List[dict])
async def get_high_risk_screenings(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get recent high-risk screenings (last 30 days)
    Only accessible by admins
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM recent_high_risk_screenings")
            
            screenings = cursor.fetchall()
            return [dict(s) for s in screenings]
            
    except Exception as e:
        logger.error(f"Error fetching high-risk screenings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch high-risk screenings"
        )

@router.get("/patient/{patient_id}/screenings", response_model=List[ScreeningResponse])
async def get_patient_screenings(
    patient_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get all screenings for a specific patient
    Only accessible by admins
    """
    try:
        with get_db_cursor() as cursor:
            # Verify patient exists
            cursor.execute(
                "SELECT id FROM users WHERE id = %s AND role = 'PATIENT'",
                (patient_id,)
            )
            patient = cursor.fetchone()
            
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            # Get all screenings
            cursor.execute(
                """
                SELECT id, user_id, age_at_screening, height_cm, weight_kg, bmi,
                       hypertension, heart_disease, ever_married, work_type,
                       residence_type, avg_glucose_level, smoking_status,
                       stroke_probability, risk_level, created_at
                FROM stroke_screenings
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (patient_id,)
            )
            
            screenings = cursor.fetchall()
            return [ScreeningResponse(**dict(s)) for s in screenings]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient screenings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patient screenings"
        )

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_admin)
):
    """
    Get overall dashboard statistics for admin
    """
    try:
        with get_db_cursor() as cursor:
            # Total patients
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'PATIENT'")
            total_patients = cursor.fetchone()["total"]
            
            # Total screenings
            cursor.execute("SELECT COUNT(*) as total FROM stroke_screenings")
            total_screenings = cursor.fetchone()["total"]
            
            # High risk count
            cursor.execute(
                "SELECT COUNT(*) as total FROM stroke_screenings WHERE risk_level = 'High'"
            )
            high_risk_count = cursor.fetchone()["total"]
            
            # Recent screenings (last 7 days)
            cursor.execute(
                """
                SELECT COUNT(*) as total 
                FROM stroke_screenings 
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """
            )
            recent_screenings = cursor.fetchone()["total"]
            
            return {
                "total_patients": total_patients,
                "total_screenings": total_screenings,
                "high_risk_count": high_risk_count,
                "recent_screenings_7days": recent_screenings
            }
            
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )
