from contextlib import asynccontextmanager
import logging
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from app.auth import verify_api_key
from app.config import AppMode, settings
from app.demo_provider import get_demo_resources, get_demo_server_status
from app.models import HealthResponse, ResourcesResponse, ServerStatusResponse
from app.proxmox_client import ProxmoxClient, ProxmoxConnectionError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.mode == AppMode.LIVE:
        settings.validate_live_config()
    yield


app = FastAPI(
    title="ProxMonitor REST API",
    description=(
        "A ProxMonitor projekt backend szolgáltatása, amely a Proxmox VE "
        "erőforrás-adatait és állapotát közvetíti a mobilalkalmazás felé."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.exception_handler(ProxmoxConnectionError)
async def proxmox_connection_exception_handler(
    request: Request, exc: ProxmoxConnectionError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "PROXMOX_CONNECTION_ERROR",
                "message": exc.message,
                "status_code": exc.status_code,
            }
        },
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Rendszerállapot"],
    summary="Backend működőképesség ellenőrzése",
    description="Nyilvános egészségügyi ellenőrző végpont a szerver elérhetőségének vizsgálatára.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="online",
        application="ProxMonitor",
        version="1.0.0",
    )


@app.get(
    "/api/v1/status",
    response_model=ServerStatusResponse,
    tags=["Proxmox Adatok"],
    summary="Szerver hardveres állapotának lekérdezése",
    description=(
        "Visszaadja a gazdagép (node) CPU, memória, háttértár kihasználtságát és üzemidejét. "
        "DEMO módban beépített mintaadatokat, LIVE módban valós Proxmox adatokat szolgáltat."
    ),
)
async def get_status(
    _authenticated: str = Depends(verify_api_key),
) -> ServerStatusResponse:
    if settings.mode == AppMode.DEMO:
        return get_demo_server_status()

    try:
        settings.validate_live_config()
    except ValueError as e:
        logger.error("Érvénytelen LIVE szerverkonfiguráció (/api/v1/status): %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Érvénytelen szerverkonfiguráció a backend oldalon.",
        )

    client = ProxmoxClient()
    return await client.get_node_status()


@app.get(
    "/api/v1/resources",
    response_model=ResourcesResponse,
    tags=["Proxmox Adatok"],
    summary="Virtuális gépek és konténerek listája",
    description=(
        "Lekérdezi a konfigurált QEMU virtuális gépeket és LXC konténereket azok "
        "futási állapotával, valamint CPU- és memóriahasználatával együtt."
    ),
)
async def get_resources(
    _authenticated: str = Depends(verify_api_key),
) -> ResourcesResponse:
    if settings.mode == AppMode.DEMO:
        return get_demo_resources()

    try:
        settings.validate_live_config()
    except ValueError as e:
        logger.error("Érvénytelen LIVE szerverkonfiguráció (/api/v1/resources): %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Érvénytelen szerverkonfiguráció a backend oldalon.",
        )

    client = ProxmoxClient()
    return await client.get_cluster_resources()
