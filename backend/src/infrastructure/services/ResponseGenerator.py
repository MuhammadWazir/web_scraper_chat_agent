"""Response generation service using LangChain and OpenAI"""
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from typing import List, Tuple, Optional
from src.domain.utils.chat_formatter import format_chat_history_tuples

class ResponseGenerationService:
    """Service for generating responses using RAG"""
    
    def __init__(self, async_client):
        self.model = ChatOpenAI(
            model="gpt-5",
            async_client=async_client
        )


    def create_chain(self, retriever, chat_history: Optional[List[Tuple[str, str]]] = None, company_name: str = "") -> RetrievalQA:
        """Create a QA chain with optional chat history context"""
        chat_history_context = format_chat_history_tuples(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""
        prompt_template = f"""{company_context}Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
{chat_history_context}
Context: {{context}}

Question: {{question}}
Helpful Answer:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        return RetrievalQA.from_chain_type(
            llm=self.model,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )
