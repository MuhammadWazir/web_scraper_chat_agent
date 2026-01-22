from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.configs.config import load_settings
from src.container import Container
from src.presentation.api.routes import client_routes, chat_routes, message_routes

# Initialize FastAPI app
app = FastAPI(title="Web Scraper Chat Agent", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load settings
settings = load_settings()

# Initialize DI container
container = Container()

# Include routers
app.include_router(client_routes.router)
app.include_router(chat_routes.router)
app.include_router(message_routes.router)


@app.get("/")
async def root():
	return {"message": "Chat Agent System Ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)