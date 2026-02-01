from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from app.databse import supabase
from pydantic import BaseModel

class SignupData(BaseModel):
    email: str
    password: str

class MessageResponse(BaseModel):
    message: str
    
class PhoneRequest(BaseModel):
    phone: str  # Format: +1234567890
    
class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str
    
class AuthResponse(BaseModel):
    message: str = "Authentication successful"
    access_token: str
    refresh_token: str
    user: dict
    
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
def signup(sign: SignupData):
    try:
        response = supabase.auth.sign_up(
            {"email": sign.email,
             "password": sign.password}
        )
        return {
            "message": "User signed up successfully",
            "access_token": response.session.access_token if response.session else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        

@router.post("/login")
def login(sign: SignupData):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": sign.email,
             "password": sign.password}
        )
        return AuthResponse(
            message="User logged in successfully",
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user={
                "id": response.user.id,
                "email": response.user.email,  # Fixed: use email instead of phone
                "created_at": str(response.user.created_at)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# PHONE OTP ROUTES

@router.post("/send-otp", response_model=MessageResponse)
async def send_otp(request: PhoneRequest):
    """
    Send OTP to phone number for signup/login
    """
    try:
        # This works for both signup and login
        response = supabase.auth.sign_in_with_otp({
            "phone": request.phone
        })
        
        return MessageResponse(
            message=f"OTP sent successfully to {request.phone}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send OTP: {str(e)}"
        )


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest):
    """
    Verify OTP and return access token
    """
    try:
        response = supabase.auth.verify_otp({
            "phone": request.phone,
            "token": request.otp,
            "type": "sms"
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP"
            )
        
        return AuthResponse(
            message="OTP verified successfully",
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user={
                "id": response.user.id,
                "phone": response.user.phone,
                "created_at": str(response.user.created_at)
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify OTP: {str(e)}"
        )


@router.post("/signout", response_model=MessageResponse)
async def signout():
    """
    Sign out the current user
    """
    try:
        supabase.auth.sign_out()
        return MessageResponse(message="Signed out successfully")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to sign out: {str(e)}"
        )


# Dependency to get the current user
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        if user.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {
            "user_id": user.user.id, 
            "email": user.user.email,
            "phone": user.user.phone
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


user_dependency = Annotated[dict, Depends(get_current_user)]