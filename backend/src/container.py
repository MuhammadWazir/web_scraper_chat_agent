"""Dependency Injection Container - wires all dependencies together"""
from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from src.infrastructure.database.config import SessionLocal
from src.infrastructure.database.repositories.client_repository_impl import ClientRepositoryImpl
from src.infrastructure.database.repositories.chat_repository_impl import ChatRepositoryImpl
from src.infrastructure.database.repositories.message_repository_impl import MessageRepositoryImpl
from src.infrastructure.services.RagService import RAGService
from src.infrastructure.services.ChatTitleService import ChatTitleService

from src.application.use_cases.client.create_client_use_case import CreateClientUseCase
from src.application.use_cases.chat.create_chat_use_case import CreateChatUseCase
from src.application.use_cases.chat.get_client_chats_use_case import GetClientChatsUseCase
from src.application.use_cases.chat.delete_chat_use_case import DeleteChatUseCase
from src.application.use_cases.message.send_message_use_case import SendMessageUseCase
from src.application.use_cases.message.get_chat_messages_use_case import GetChatMessagesUseCase


class Container(containers.DeclarativeContainer):
    """Dependency injection container"""
    
    # Configuration
    config = providers.Configuration()
    
    # Database session factory
    db_session = providers.Factory(SessionLocal)
    
    # Repositories - scoped to database session
    client_repository = providers.Factory(
        ClientRepositoryImpl,
        db=db_session
    )
    
    chat_repository = providers.Factory(
        ChatRepositoryImpl,
        db=db_session
    )
    
    message_repository = providers.Factory(
        MessageRepositoryImpl,
        db=db_session
    )
    
    # Domain Services - singleton
    rag_service = providers.Singleton(RAGService)
    
    chat_title_service = providers.Singleton(ChatTitleService)
    
    # Use Cases - factory (create new instance for each use)
    create_client_use_case = providers.Factory(
        CreateClientUseCase,
        client_repository=client_repository,
        rag_service=rag_service
    )
    
    create_chat_use_case = providers.Factory(
        CreateChatUseCase,
        chat_repository=chat_repository,
        client_repository=client_repository
    )
    
    get_client_chats_use_case = providers.Factory(
        GetClientChatsUseCase,
        chat_repository=chat_repository,
        client_repository=client_repository
    )
    
    delete_chat_use_case = providers.Factory(
        DeleteChatUseCase,
        chat_repository=chat_repository
    )
    
    send_message_use_case = providers.Factory(
        SendMessageUseCase,
        message_repository=message_repository,
        chat_repository=chat_repository,
        client_repository=client_repository,
        rag_service=rag_service,
        chat_title_service=chat_title_service
    )
    
    get_chat_messages_use_case = providers.Factory(
        GetChatMessagesUseCase,
        message_repository=message_repository
    )
