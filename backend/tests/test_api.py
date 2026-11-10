"""FastAPI végpontok automatizált integrációs és egységtesztjei."""

import httpx
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.config import settings, AppMode
from app.models import (
    CpuStatus,
    MemoryStatus,
    StorageStatus,
    StoragePoolItem,
    ServerStatusResponse,
    ResourceItem,
    ResourcesResponse,
)
from app.proxmox_client import ProxmoxClient, ProxmoxConnectionError


# Tesztekhez egyedi, nem alapértelmezett API-kulcsot állítunk be
VALID_API_KEY = "teszt-egyedi-api-kulcs-2026"
settings.api_key = VALID_API_KEY
settings.mode = AppMode.DEMO

client = TestClient(app)

AUTH_HEADERS = {"X-API-Key": VALID_API_KEY}
BEARER_HEADERS = {"Authorization": f"Bearer {VALID_API_KEY}"}


@pytest.fixture(autouse=True)
def restore_settings():
    """Minden teszt előtt és után visszaállítja az alapértelmezett tesztbeállításokat."""
    settings.mode = AppMode.DEMO
    settings.api_key = VALID_API_KEY
    settings.proxmox_host = "https://192.168.1.99:8006"
    settings.proxmox_node = "pve"
    settings.proxmox_token_id = "user@pam!token"
    settings.proxmox_token_secret = "secret-uuid"
    yield
    settings.mode = AppMode.DEMO
    settings.api_key = VALID_API_KEY


# ==============================================================================
# 1. /health végpont tesztek
# ==============================================================================

def test_health_check_returns_200():
    """A /health végpont hitelesítés nélkül is elérhető és helyes JSON-t ad."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["application"] == "ProxMonitor"
    assert data["version"] == "0.3.0"


# ==============================================================================
# 2. Hitelesítési tesztek (Hiányzó és Hibás kulcs)
# ==============================================================================

def test_status_missing_auth_returns_401():
    """Hiányzó hitelesítő fejléccel a /api/v1/status 401-es kódot ad."""
    response = client.get("/api/v1/status")
    assert response.status_code == 401
    assert "Hitelesítés szükséges" in response.json()["detail"]


def test_status_invalid_auth_returns_401():
    """Hibás API kulccsal a /api/v1/status 401-es kódot ad."""
    response = client.get("/api/v1/status", headers={"X-API-Key": "hibas-kulcs-123"})
    assert response.status_code == 401
    assert "Érvénytelen API kulcs" in response.json()["detail"]


def test_resources_missing_auth_returns_401():
    """Hiányzó hitelesítő fejléccel a /api/v1/resources 401-es kódot ad."""
    response = client.get("/api/v1/resources")
    assert response.status_code == 401


def test_resources_invalid_bearer_returns_401():
    """Hibás Bearer tokennel a /api/v1/resources 401-es kódot ad."""
    response = client.get(
        "/api/v1/resources",
        headers={"Authorization": "Bearer rossz-bearer-token"}
    )
    assert response.status_code == 401


# ==============================================================================
# 3. Sikeres lekérdezések (DEMO üzemmód)
# ==============================================================================

def test_status_demo_mode_success():
    """DEMO módban érvényes hitelesítéssel a válasz helyes és a mintaadatokat tartalmazza."""
    # Biztosítjuk, hogy DEMO módban vagyunk
    settings.mode = AppMode.DEMO

    response = client.get("/api/v1/status", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()

    assert data["mode"] == "DEMO"
    assert data["node_name"] == "pve-demo-node"
    assert data["cpu"]["usage_percent"] == 24.0
    assert data["memory"]["formatted"] == "8.2 GB / 16 GB"
    assert data["storage"]["formatted"] == "1.8 TB / 4 TB"
    assert "uptime_seconds" in data
    assert "uptime_formatted" in data


def test_resources_demo_mode_success():
    """DEMO módban Bearer tokennel a virtuális gépek listája sikeresen megérkezik."""
    settings.mode = AppMode.DEMO

    response = client.get("/api/v1/resources", headers=BEARER_HEADERS)
    assert response.status_code == 200
    data = response.json()

    assert data["mode"] == "DEMO"
    resources = data["resources"]
    assert len(resources) == 3

    # Az Android UI-nak megfelelő elemek ellenőrzése
    names = [r["name"] for r in resources]
    assert "Home Assistant" in names
    assert "Jellyfin" in names
    assert "AdGuard Home" in names

    first = resources[0]
    assert first["vmid"] == 100
    assert first["type"] == "VM"
    assert first["display_status"] == "Online"


# ==============================================================================
# 4. LIVE üzemmód: Konfigurációs és Proxmox kapcsolati hibák
# ==============================================================================

def test_live_mode_missing_config_returns_500():
    """Ha LIVE módban nincsenek beállítva a Proxmox adatok, 500-as hibát kapunk."""
    settings.mode = AppMode.LIVE
    settings.proxmox_host = None
    settings.proxmox_token_id = None
    settings.proxmox_token_secret = None

    response = client.get("/api/v1/status", headers=AUTH_HEADERS)
    assert response.status_code == 500
    assert "Érvénytelen szerverkonfiguráció" in response.json()["detail"]

    # Visszaállítjuk DEMO-ra a többi teszthez
    settings.mode = AppMode.DEMO


def test_live_mode_unreachable_proxmox_returns_502_and_no_demo_leak():
    """
    FONTOS KÖVETELMÉNY:
    Ha a LIVE módban a Proxmox nem elérhető, az API-nak 502/504 hibával kell visszatérnie,
    és SOHA nem térhet vissza észrevétlenül a mintaadatokra!
    """
    settings.mode = AppMode.LIVE
    settings.proxmox_host = "https://192.168.1.99:8006"
    settings.proxmox_token_id = "user@pam!token"
    settings.proxmox_token_secret = "secret-uuid"

    # Szimuláljuk a sikertelen hálózati kapcsolatot
    with patch(
        "app.proxmox_client.ProxmoxClient.get_node_status",
        new_callable=AsyncMock,
        side_effect=ProxmoxConnectionError(
            "Nem sikerült csatlakozni a Proxmox szerverhez.",
            status_code=502,
        ),
    ):
        response = client.get("/api/v1/status", headers=AUTH_HEADERS)

        # Ellenőrizzük, hogy nem 200 (nem esett vissza mintaadatra!)
        assert response.status_code == 502
        err_data = response.json()
        assert "error" in err_data
        assert err_data["error"]["type"] == "PROXMOX_CONNECTION_ERROR"
        assert "Nem sikerült csatlakozni" in err_data["error"]["message"]


@pytest.mark.parametrize(
    "insecure_key",
    [
        "",
        "   ",
        "titkos-mobil-api-kulcs-valtoztasd-meg",
        "changeme",
    ],
)
def test_live_mode_rejects_default_or_known_api_keys(insecure_key: str):
    """LIVE módban a backend nem indulhat el / nem szolgálhat ki kérést ismert alapértelmezett API-kulccsal."""
    settings.mode = AppMode.LIVE
    settings.api_key = insecure_key

    with pytest.raises(ValueError):
        settings.validate_live_config()

    if insecure_key.strip():
        response = client.get("/api/v1/status", headers={"X-API-Key": insecure_key.strip()})
        assert response.status_code == 500
        assert "Érvénytelen szerverkonfiguráció" in response.json()["detail"]


def test_live_mode_status_and_resources_success():
    """LIVE módban sikeres Proxmox válasz esetén a végpontok LIVE adatokat adnak vissza."""
    settings.mode = AppMode.LIVE

    mock_status = ServerStatusResponse(
        mode="LIVE",
        node_name="prox",
        uptime_seconds=86400,
        uptime_formatted="1 nap, 0 óra, 0 perc",
        cpu=CpuStatus(usage_percent=12.4, cores=12),
        memory=MemoryStatus(
            used_bytes=4294967296,
            total_bytes=17179869184,
            formatted="4.0 GB / 16.0 GB",
            usage_percent=25.0,
        ),
        storage=StorageStatus(
            used_bytes=21474836480,
            total_bytes=68719476736,
            formatted="20.0 GB / 64.0 GB",
            usage_percent=31.3,
        ),
        storage_pools=[
            StoragePoolItem(
                name="local-lvm",
                type="lvmthin",
                used_bytes=53687091200,
                total_bytes=107374182400,
                formatted="50.0 GB / 100.0 GB",
                usage_percent=50.0,
                content="images,rootdir",
            )
        ],
    )

    mock_resources = ResourcesResponse(
        mode="LIVE",
        resources=[
            ResourceItem(
                vmid=100,
                name="haos",
                type="VM",
                raw_type="qemu",
                status="running",
                display_status="Online",
                cpu_percent=4.5,
                memory_used_bytes=4294967296,
                memory_formatted="4.0 GB / 4.0 GB",
            )
        ],
    )

    with patch(
        "app.proxmox_client.ProxmoxClient.get_node_status",
        new_callable=AsyncMock,
        return_value=mock_status,
    ), patch(
        "app.proxmox_client.ProxmoxClient.get_cluster_resources",
        new_callable=AsyncMock,
        return_value=mock_resources,
    ):
        status_resp = client.get("/api/v1/status", headers=AUTH_HEADERS)
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["mode"] == "LIVE"
        assert status_data["node_name"] == "prox"
        assert status_data["cpu"]["cores"] == 12
        assert len(status_data["storage_pools"]) == 1

        res_resp = client.get("/api/v1/resources", headers=AUTH_HEADERS)
        assert res_resp.status_code == 200
        res_data = res_resp.json()
        assert res_data["mode"] == "LIVE"
        assert len(res_data["resources"]) == 1
        assert res_data["resources"][0]["name"] == "haos"


@pytest.mark.asyncio
async def test_proxmox_client_does_not_leak_internal_host_or_raw_error():
    """A ProxmoxClient hiba esetén nem szivárogtathatja ki a belső Proxmox IP-t vagy nyers hibaüzenetet."""
    settings.mode = AppMode.LIVE
    settings.proxmox_host = "https://10.99.88.77:8006"
    proxmox = ProxmoxClient()

    mock_client_instance = AsyncMock()
    mock_client_instance.get.side_effect = httpx.ConnectError("Connection refused to 10.99.88.77:8006")
    mock_client_cm = MagicMock()
    mock_client_cm.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client_cm):
        with pytest.raises(ProxmoxConnectionError) as exc_info:
            await proxmox.get_node_status()

        assert "10.99.88.77" not in exc_info.value.message
        assert "Connection refused" not in exc_info.value.message
        assert exc_info.value.status_code == 502
