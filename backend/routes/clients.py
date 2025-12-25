from fastapi import APIRouter, HTTPException
from services.rag_pipeline_service import RAGPipeline
from dtos.create_client_dto import CreateClientDTO
from dtos.query_client_dto import QueryClientDTO
router = APIRouter(prefix="", tags=["clients"])


@router.post("/create-client", response_model=CreateClientDTO)
async def create_client(request: CreateClientDTO):
	rag_pipeline = RAGPipeline()
	await rag_pipeline.build(request.website_url, request.company_name)
	return True

@router.post("/query-client", response_model=str)
async def query_client(request: QueryClientDTO):
	rag_pipeline = RAGPipeline()
	response = await rag_pipeline.query(request.question, request.company_name)
	return response


