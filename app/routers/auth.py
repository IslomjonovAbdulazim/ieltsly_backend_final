from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.auth import authenticate_admin, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AdminLogin(BaseModel):
    admin_pass_key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(login_data: AdminLogin):
    if not authenticate_admin(login_data.admin_pass_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin pass key"
        )
    
    access_token = create_access_token(data={"role": "admin"})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }