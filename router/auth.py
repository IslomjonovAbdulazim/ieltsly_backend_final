from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth import verify_admin_credentials, create_access_token
from datetime import timedelta

router = APIRouter()

class AdminLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/admin/login", response_model=Token)
def admin_login(credentials: AdminLogin):
    if not verify_admin_credentials(credentials.phone, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    
    access_token = create_access_token(
        data={"sub": credentials.phone},
        expires_delta=timedelta(hours=24)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}