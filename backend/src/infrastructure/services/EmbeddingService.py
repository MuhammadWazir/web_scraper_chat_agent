from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    def get_embeddings(self):
        """Get the embeddings instance"""
        return self.embeddings
