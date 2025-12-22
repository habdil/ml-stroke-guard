"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime, date
from enum import Enum

# ============================================
# ENUMS (matching database)
# ============================================

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PATIENT = "PATIENT"

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class WorkType(str, Enum):
    PRIVATE = "Private"
    SELF_EMPLOYED = "Self-employed"
    GOVT_JOB = "Govt_job"
    CHILDREN = "children"
    NEVER_WORKED = "Never_worked"

class ResidenceType(str, Enum):
    URBAN = "Urban"
    RURAL = "Rural"

class SmokingStatus(str, Enum):
    FORMERLY_SMOKED = "formerly smoked"
    NEVER_SMOKED = "never smoked"
    SMOKES = "smokes"
    UNKNOWN = "Unknown"

# ============================================
# AUTH MODELS
# ============================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    date_of_birth: date
    gender: Gender
    phone_number: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    date_of_birth: date
    gender: Gender
    phone_number: Optional[str]
    role: UserRole
    created_at: datetime

# ============================================
# SCREENING MODELS
# ============================================

class ScreeningInput(BaseModel):
    """Input untuk screening (dari frontend)"""
    height_cm: float = Field(..., ge=50, le=250)
    weight_kg: float = Field(..., ge=20, le=300)
    hypertension: bool
    heart_disease: bool
    ever_married: bool
    work_type: WorkType
    residence_type: ResidenceType
    avg_glucose_level: float = Field(..., ge=50, le=400)
    smoking_status: SmokingStatus

class ScreeningResponse(BaseModel):
    """Response setelah screening"""
    id: str
    user_id: str
    age_at_screening: int
    height_cm: float
    weight_kg: float
    bmi: float
    hypertension: bool
    heart_disease: bool
    ever_married: bool
    work_type: WorkType
    residence_type: ResidenceType
    avg_glucose_level: float
    smoking_status: SmokingStatus
    stroke_probability: float
    risk_level: RiskLevel
    created_at: datetime

class ScreeningSummary(BaseModel):
    """Summary untuk list screenings"""
    id: str
    age_at_screening: int
    bmi: float
    risk_level: RiskLevel
    stroke_probability: float
    created_at: datetime

# ============================================
# ADMIN MODELS
# ============================================

class PatientSummary(BaseModel):
    """Summary pasien untuk admin dashboard"""
    id: str
    full_name: str
    email: str
    date_of_birth: date
    gender: Gender
    total_screenings: int
    last_screening_date: Optional[datetime]
    highest_risk_level: Optional[RiskLevel]

class ScreeningStatistics(BaseModel):
    """Statistik screening"""
    risk_level: RiskLevel
    total_count: int
    avg_age: float
    avg_bmi: float
    avg_glucose: float
    avg_probability: float
    hypertension_count: int
    heart_disease_count: int
