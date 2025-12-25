from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List
from configs.constants import PERSIST_DIR
class VectorStore:
    def __init__(self, embeddings, persist_dir: str = PERSIST_DIR):
        self.embeddings = embeddings
        self.persist_dir = persist_dir

    def create_store(self, documents: List[Document], collection_name: str) -> Chroma:
        # Persist collection on disk
        return Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory=self.persist_dir
        )

    def load_store(self, collection_name: str) -> Chroma:
        # Load existing persistent collection
        return Chroma(
            embedding_function=self.embeddings,
            collection_name=collection_name,
            persist_directory=self.persist_dir
        )
