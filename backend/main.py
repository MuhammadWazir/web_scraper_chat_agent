from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
from src.configs.config import load_settings
from src.container import Container
from src.presentation.api.routes import client_routes, chat_routes, message_routes, widget_routes, auth_routes
from src.infrastructure.database.config import session_id_var, SessionLocal

app = FastAPI(
    title="Web Scraper Chat Agent", 
    version="2.0.0",
    root_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # Set a unique session ID for this request scope
    token = str(uuid.uuid4())
    session_id_var.set(token)
    try:
        response = await call_next(request)
        return response
    finally:
        # Close the session and return connection to pool
        SessionLocal.remove()

# Load settings
settings = load_settings()

# Initialize DI container
container = Container()

# Include routers
app.include_router(auth_routes.router)
app.include_router(client_routes.router)
app.include_router(chat_routes.router)
app.include_router(message_routes.router)
app.include_router(widget_routes.router)


@app.get("/")
async def root():
	return {"message": "Chat Agent System Ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)