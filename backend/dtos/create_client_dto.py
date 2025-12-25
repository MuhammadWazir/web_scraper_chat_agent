from pydantic import BaseModel

class CreateClientDTO(BaseModel):
    company_name: str
    website_url: str
