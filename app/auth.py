from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import security
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from typing import Annotated
from app.databse import supabase
from pydantic import BaseModel

class SignupData(BaseModel):
    email: str
    password: str
    
security=HTTPBearer()
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
        return {
            "message": "User logged in successfully",
            "token_type":"bearer",
            "access_token": response.session.access_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
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
        return {"user_id": user.user.id, "email": user.user.email}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
        
user_dependency=Annotated[dict,Depends(get_current_user)]