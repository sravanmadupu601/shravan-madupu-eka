import uvicorn

from app.config.settings import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.mcp_service_host,
        port=settings.mcp_service_port,
    )
