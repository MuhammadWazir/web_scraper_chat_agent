from pydantic import BaseModel

class QueryClientDTO(BaseModel):
    company_name: str
    question: str