from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    def get_embeddings(self):
        return self.embeddings