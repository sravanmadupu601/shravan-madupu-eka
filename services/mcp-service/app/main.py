from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.routing import Mount

from app.api.dependencies import get_mcp_application_service
from app.api.routes.health import router as health_router
from app.config.settings import settings
from app.infrastructure.mcp.server import create_mcp_server

mcp_server = create_mcp_server(
    get_mcp_application_service(),
    settings.app_name,
    settings.mcp_service_host,
    settings.mcp_service_port,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with mcp_server.session_manager.run():
        yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.include_router(health_router)
app.router.routes.append(Mount("/", app=mcp_server.streamable_http_app()))
