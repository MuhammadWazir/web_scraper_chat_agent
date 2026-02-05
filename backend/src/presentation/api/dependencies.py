"""FastAPI dependencies - provides instances from container"""
from typing import Callable
from container import Container


def get_container() -> Container:
    """Get the DI container instance"""
    return Container()


def get_use_case_provider(use_case_name: str) -> Callable:
    """Generic dependency provider for use cases"""
    def provider(container: Container = get_container()):
        return getattr(container, use_case_name)()
    return provider
