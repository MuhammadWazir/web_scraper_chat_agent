"""Delete client use case"""
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.clients.abstract_vector_store_client import AbstractVectorStoreClient


class DeleteClientUseCase:
    """Use case for deleting a client from both database and Qdrant"""
    
    def __init__(self, client_repository: IClientRepository, vector_store_client: AbstractVectorStoreClient):
        self.client_repository = client_repository
        self.vector_store_client = vector_store_client
    
    def execute(self, client_id: str) -> bool:
        """
        Delete a client and their associated Qdrant collection
        
        Args:
            client_id: The client ID to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValueError: If client not found
        """
        # First, check if client exists
        client = self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Delete from Qdrant (collection name is based on client_name)
        collection_name = client.client_name
        try:
            self.vector_store_client.delete_collection(collection_name)
        except Exception as e:
            # Log the error but continue with database deletion
            print(f"Warning: Could not delete Qdrant collection {collection_name}: {str(e)}")
        
        # Delete from database
        success = self.client_repository.delete(client_id)
        
        if not success:
            raise ValueError(f"Failed to delete client {client_id} from database")
        
        return True
