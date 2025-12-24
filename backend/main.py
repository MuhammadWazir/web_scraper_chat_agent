from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs.config import load_settings
from routes.clients import router as clients_router

app = FastAPI(title="Web Scraper Voice Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = load_settings()

app.include_router(clients_router)

@app.get("/")
async def root():
	return {"message": "Voice Agent System Ready"}


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000) 