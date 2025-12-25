from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

class ResponseGenerationService:
    def __init__(self, async_client):
        self.model = ChatOpenAI(
            model="gpt-5",
            temperature=0.2,
            async_client=async_client
        )

    def create_chain(self, retriever) -> RetrievalQA:
        return RetrievalQA.from_chain_type(
            llm=self.model,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=False
        )

