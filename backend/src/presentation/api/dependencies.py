"""FastAPI dependencies - provides instances from container"""
from typing import Callable
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.container import Container
from src.domain.auth.jwt_handler import verify_token, security


def get_container() -> Container:
    """Get the DI container instance"""
    return Container()


def get_use_case_provider(use_case_name: str) -> Callable:
    """Generic dependency provider for use cases"""
    def provider(container: Container = get_container()):
        return getattr(container, use_case_name)()
    return provider


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return current user - use this to protect routes"""
    return verify_token(credentials)
