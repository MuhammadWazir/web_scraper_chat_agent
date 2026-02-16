"""Login response DTO"""
from pydantic import BaseModel


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str
