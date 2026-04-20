from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Emergency Exit — Notification Service",
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to app domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and container orchestration."""
    return {"status": "ok", "service": "notification-service"}


# TODO: Import and include routers from app.api
# from app.api.routes import router
# app.include_router(router, prefix="/api/v1")
