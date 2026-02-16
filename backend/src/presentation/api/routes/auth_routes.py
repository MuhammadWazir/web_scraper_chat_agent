from fastapi import APIRouter, HTTPException
from src.configs.config import load_settings
from src.application.dtos.requests.login_request import LoginRequest
from src.application.dtos.responses.login_response import LoginResponse
from src.domain.auth.jwt_handler import create_access_token

router = APIRouter(prefix="", tags=["auth"])

settings = load_settings()


@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """Admin login endpoint - validates credentials and returns JWT token"""
    if request.username == settings.admin_username and request.password == settings.admin_password:
        # Create JWT token
        access_token = create_access_token(data={"sub": request.username})
        
        return LoginResponse(
            success=True, 
            message="Login successful",
            token=access_token
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

