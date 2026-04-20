"""
API Gateway — single entry point for all Emergency Exit services.

Responsibilities:
- JWT token validation
- Rate limiting (100 req/min per user)
- Request routing to downstream services
- CORS configuration
- Request/response logging
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog
import time

logger = structlog.get_logger()

app = FastAPI(
    title="Emergency Exit — API Gateway",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry — maps path prefixes to downstream URLs
SERVICE_REGISTRY = {
    "/api/v1/auth": "http://identity-service:8001",
    "/api/v1/users": "http://identity-service:8001",
    "/api/v1/assets": "http://vault-service:8002",
    "/api/v1/will": "http://vault-service:8002",
    "/api/v1/documents": "http://vault-service:8002",
    "/api/v1/wishes": "http://wishes-service:8003",
    "/api/v1/messages": "http://wishes-service:8003",
    "/api/v1/guardians": "http://guardian-service:8004",
    "/api/v1/checkin": "http://pulse-service:8005",
    "/api/v1/config": "http://pulse-service:8005",
    "/api/v1/notify": "http://notification-service:8006",
}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with timing."""
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(
        "request",
        method=request.method,
        path=str(request.url.path),
        status=response.status_code,
        duration_ms=duration,
    )
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "api-gateway"}


# TODO: Implement proxy routing with httpx
# TODO: Implement JWT validation middleware
# TODO: Implement rate limiting (100 req/min per user)
