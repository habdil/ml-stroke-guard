"""
Authentication router (register, login)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import UserRegister, UserLogin, Token, UserResponse
from app.auth import get_password_hash, verify_password, create_access_token
from app.database import get_db_cursor
from app.dependencies import get_current_user
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    Register new patient user
    """
    try:
        # Check if email already exists
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (user.email,)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password
            hashed_password = get_password_hash(user.password)
            
            # Insert new user
            cursor.execute(
                """
                INSERT INTO users (
                    email, password, full_name, date_of_birth, 
                    gender, phone_number, role
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'PATIENT')
                RETURNING id, email, full_name, date_of_birth, 
                          gender, phone_number, role, created_at
                """,
                (
                    user.email,
                    hashed_password,
                    user.full_name,
                    user.date_of_birth,
                    user.gender.value,
                    user.phone_number
                )
            )
            
            new_user = cursor.fetchone()
            logger.info(f"New user registered: {user.email}")
            
            return UserResponse(**dict(new_user))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login user and return JWT token
    """
    try:
        with get_db_cursor() as cursor:
            # Get user by email
            cursor.execute(
                """
                SELECT id, email, password, role 
                FROM users 
                WHERE email = %s
                """,
                (credentials.email,)
            )
            user = cursor.fetchone()
            
            # Verify user exists and password is correct
            if not user or not verify_password(credentials.password, user["password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token = create_access_token(
                data={"sub": user["email"], "role": user["role"]}
            )
            
            logger.info(f"User logged in: {credentials.email}")
            
            return Token(access_token=access_token)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info
    """
    return UserResponse(**current_user)

