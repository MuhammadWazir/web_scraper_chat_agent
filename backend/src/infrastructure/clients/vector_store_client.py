"""Qdrant vector store client implementation"""
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from src.configs.config import load_settings
from src.domain.abstractions.clients.abstract_vector_store_client import AbstractVectorStoreClient
from src.domain.entities.vector_search_result import VectorSearchResult


class VectorStoreClient(AbstractVectorStoreClient):
    """Qdrant implementation of vector store client"""
    
    def __init__(self):
        settings = load_settings()
        self.client = QdrantClient(
            url=settings.qdrant_cluster_endpoint,
            api_key=settings.qdrant_api_key
        )

    def ensure_collection(
        self, 
        collection_name: str, 
        vector_size: int = 1536, 
        distance: str = "Cosine"
    ) -> None:
        """Ensure a collection exists, create if it doesn't"""
        try:
            if not self.client.collection_exists(collection_name=collection_name):
                distance_metric = Distance.COSINE if distance == "Cosine" else Distance.EUCLID
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=distance_metric)
                )
        except Exception as e:
            raise Exception(f"Error ensuring collection {collection_name}: {str(e)}")

    def upload(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None,
        vector_size: Optional[int] = None
    ) -> str:
        """Upload embeddings with metadata to a collection"""
        try:
            if not self.client.collection_exists(collection_name=collection_name):
                self.ensure_collection(
                    collection_name, 
                    vector_size=vector_size or len(embeddings[0])
                )

            points = []
            for i, (vec, meta) in enumerate(zip(embeddings, metadatas)):
                point_id = ids[i] if ids else i
                points.append(PointStruct(id=point_id, vector=vec, payload=meta))

            self.client.upsert(collection_name=collection_name, points=points)
            return collection_name
        except Exception as e:
            raise Exception(f"Error uploading to collection {collection_name}: {str(e)}")

    def search_chunks(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[VectorSearchResult]:
        """Search for similar chunks in a collection"""
        try:
            search_results = self.client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=limit
            )
            
            results = []
            for hit in search_results.points:
                results.append(VectorSearchResult(
                    text=hit.payload.get("original_text") or hit.payload.get("text") or "",
                    score=hit.score,
                    chunk_index=hit.payload.get("chunk_index"),
                    metadata=hit.payload
                ))
            
            return results
        except Exception as e:
            raise Exception(f"Error searching chunks in {collection_name}: {str(e)}")

    def search_all_collections(
        self,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[VectorSearchResult]:
        """Search across all collections"""
        try:
            results = []
            collections_response = self.client.get_collections()
            collection_names = [col.name for col in collections_response.collections]

            for collection_name in collection_names:
                search_results = self.client.query_points(
                    collection_name=collection_name,
                    query=query_embedding,
                    limit=limit
                )
                for hit in search_results.points:
                    # Add collection name to metadata
                    metadata = dict(hit.payload)
                    metadata["collection"] = collection_name
                    
                    results.append(VectorSearchResult(
                        text=hit.payload.get("original_text") or hit.payload.get("text") or "",
                        score=hit.score,
                        chunk_index=hit.payload.get("chunk_index"),
                        metadata=metadata
                    ))

            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]
        except Exception as e:
            raise Exception(f"Error searching chunks: {str(e)}")

    def delete_collection(self, collection_name: str) -> Dict:
        """Delete a collection"""
        try:
            if self.client.collection_exists(collection_name):
                self.client.delete_collection(collection_name=collection_name)
                return {"success": True, "message": f"Collection {collection_name} deleted."}
            else:
                raise Exception(f"Collection {collection_name} does not exist.")
        except Exception as e:
            raise Exception(f"Error deleting collection {collection_name}: {str(e)}")

    def list_collections(self) -> List[str]:
        """List all available collections"""
        try:
            collections_response = self.client.get_collections()
            return [col.name for col in collections_response.collections]
        except Exception as e:
            raise Exception(f"Error listing collections: {str(e)}")
