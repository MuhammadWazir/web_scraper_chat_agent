"""Vector store service using Qdrant"""
from typing import List, Dict
from langchain.schema import Document
from src.infrastructure.clients.vector_store_client import VectorStoreClient


class VectorStoreService:
    """Service for managing vector stores with Qdrant"""
    
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vector_client = VectorStoreClient()

    def create_store(self, documents: List[Document], collection_name: str) -> str:
        """Create and populate a new vector store collection"""
        # Extract texts and metadata from documents
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Generate embeddings
        embeddings_list = []
        for text in texts:
            embedding = self.embeddings.embed_query(text)
            embeddings_list.append(embedding)
        
        # Enrich metadata with text content
        for i, meta in enumerate(metadatas):
            meta["text"] = texts[i]
            meta["original_text"] = texts[i]
        
        # Upload to Qdrant
        self.vector_client.upload(
            collection_name=collection_name,
            embeddings=embeddings_list,
            metadatas=metadatas,
            vector_size=len(embeddings_list[0]) if embeddings_list else 1536
        )
        
        return collection_name

    def search(self, query: str, collection_name: str, k: int = 3) -> List[Dict]:
        """Search for similar documents in a collection"""
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Qdrant
        results = self.vector_client.search_chunks(
            collection_name=collection_name,
            query_embedding=query_embedding,
            limit=k
        )
        
        return results

    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        return self.vector_client.delete_collection(collection_name)

    def list_collections(self) -> List[str]:
        """List all available collections"""
        return self.vector_client.list_collections()

