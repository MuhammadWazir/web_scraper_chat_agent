"""Dependency Injection Container - wires all dependencies together"""
from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from src.infrastructure.database.config import SessionLocal
from src.infrastructure.database.repositories.client_repository import ClientRepository
from src.infrastructure.database.repositories.chat_repository import ChatRepository
from src.infrastructure.database.repositories.message_repository import MessageRepository
from src.infrastructure.database.repositories.widget_session_repository import WidgetSessionRepository
from src.infrastructure.services.RagService import RAGService
from src.infrastructure.services.ChatTitleService import ChatTitleService

from src.application.use_cases.client.create_client_use_case import CreateClientUseCase
from src.application.use_cases.client.update_client_use_case import UpdateClientUseCase
from src.application.use_cases.client.get_client_use_case import GetClientUseCase
from src.application.use_cases.client.get_all_clients_use_case import GetAllClientsUseCase
from src.application.use_cases.chat.create_chat_use_case import CreateChatUseCase
from src.application.use_cases.chat.get_client_chats_use_case import GetClientChatsUseCase
from src.application.use_cases.chat.delete_chat_use_case import DeleteChatUseCase
from src.application.use_cases.message.send_message_use_case import SendMessageUseCase
from src.application.use_cases.message.get_chat_messages_use_case import GetChatMessagesUseCase
from src.application.use_cases.widget.generate_widget_url_use_case import GenerateWidgetUrlUseCase
from src.application.use_cases.widget.initialize_widget_session_use_case import InitializeWidgetSessionUseCase
from src.application.use_cases.widget.validate_widget_session_use_case import ValidateWidgetSessionUseCase
from src.application.use_cases.widget.get_widget_chats_use_case import GetWidgetChatsUseCase
from src.application.use_cases.widget.create_widget_chat_use_case import CreateWidgetChatUseCase
from src.application.use_cases.widget.delete_widget_chat_use_case import DeleteWidgetChatUseCase
from src.application.use_cases.widget.send_widget_message_use_case import SendWidgetMessageUseCase


class Container(containers.DeclarativeContainer):
    """Dependency injection container"""
    
    # Configuration
    config = providers.Configuration()
    
    # Database session factory
    db_session = providers.Factory(SessionLocal)
    
    # Repositories - scoped to database session
    client_repository = providers.Singleton(
        ClientRepository,
        db=db_session
    )
    
    chat_repository = providers.Singleton(
        ChatRepository,
        db=db_session
    )
    
    message_repository = providers.Singleton(
        MessageRepository,
        db=db_session
    )
    
    widget_session_repository = providers.Singleton(
        WidgetSessionRepository,
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

    update_client_use_case = providers.Factory(
        UpdateClientUseCase,
        client_repository=client_repository
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
    
    get_client_use_case = providers.Factory(
        GetClientUseCase,
        client_repository=client_repository
    )
    
    get_all_clients_use_case = providers.Factory(
        GetAllClientsUseCase,
        client_repository=client_repository
    )
    
    generate_widget_url_use_case = providers.Factory(
        GenerateWidgetUrlUseCase,
        widget_session_repository=widget_session_repository,
        client_repository=client_repository
    )
    
    initialize_widget_session_use_case = providers.Factory(
        InitializeWidgetSessionUseCase,
        widget_session_repository=widget_session_repository
    )
    
    validate_widget_session_use_case = providers.Factory(
        ValidateWidgetSessionUseCase,
        widget_session_repository=widget_session_repository
    )
    
    get_widget_chats_use_case = providers.Factory(
        GetWidgetChatsUseCase,
        widget_session_repository=widget_session_repository,
        chat_repository=chat_repository
    )
    
    create_widget_chat_use_case = providers.Factory(
        CreateWidgetChatUseCase,
        widget_session_repository=widget_session_repository,
        chat_repository=chat_repository,
        client_repository=client_repository
    )
    
    delete_widget_chat_use_case = providers.Factory(
        DeleteWidgetChatUseCase,
        widget_session_repository=widget_session_repository,
        chat_repository=chat_repository
    )
    
    send_widget_message_use_case = providers.Factory(
        SendWidgetMessageUseCase,
        widget_session_repository=widget_session_repository,
        chat_repository=chat_repository,
        message_repository=message_repository,
        client_repository=client_repository,
        rag_service=rag_service,
        chat_title_service=chat_title_service
    )

