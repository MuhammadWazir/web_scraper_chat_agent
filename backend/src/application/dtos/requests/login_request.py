"""Login request DTO"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
