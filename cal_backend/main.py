from fastapi import FastAPI, HTTPException, Header, Request, Response
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Cal Backend API")

# Store Cal credentials
CAL_CLIENT_API_KEY = os.getenv("CAL_CLIENT_API_KEY")
CAL_AUTH_TOKEN = os.getenv("CAL_AUTH_TOKEN")

# Base URL for the main backend
MAIN_BACKEND_URL = os.getenv("MAIN_BACKEND_URL", "http://localhost:8000")


class SessionRequest(BaseModel):
    pass


class SessionResponse(BaseModel):
    session_token: str


@app.get("/")
async def root():
    return {"status": "ok", "service": "cal_backend"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/generate-session", response_model=SessionResponse)
async def generate_session(authorization: str = Header(None)):
    """Generate a widget session token using Cal's credentials."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Validate the authorization token (simple check against Cal's auth token)
    expected_token = f"Bearer {CAL_AUTH_TOKEN.replace('Bearer ', '')}" if CAL_AUTH_TOKEN else None
    if authorization != expected_token and authorization != CAL_AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    
    try:
        # Call the main backend to generate widget URL with Cal's API key
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MAIN_BACKEND_URL}/widget/generate-url",
                headers={"X-Api-Key": CAL_CLIENT_API_KEY}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to generate session")
            
            data = response.json()
            return SessionResponse(session_token=data.get("session_token"))
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_backend(path: str, request: Request):
    """Proxy all other requests to the main backend, adding Cal's auth token."""
    # Build the target URL
    target_url = f"{MAIN_BACKEND_URL}/{path}"
    
    # Get the request body
    body = await request.body()
    
    # Prepare headers - add Cal's auth token
    headers = dict(request.headers)
    body["authorization"] = CAL_AUTH_TOKEN
    
    # Ensure X-Forwarded-For is preserved (for IP-based session validation)
    # Get the original client IP from X-Forwarded-For or fallback to client host
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    client_host = request.client.host if request.client else None
    original_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else client_host
    if original_ip:
        headers["X-Forwarded-For"] = original_ip
    
    # Remove host header (will be set automatically)
    headers.pop("host", None)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                timeout=httpx.Timeout(3600.0)  # 1 hour timeout for streaming
            )
            
        # Return the response with the same status code
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")
