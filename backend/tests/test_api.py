"""FastAPI végpontok automatizált integrációs és egységtesztjei."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings, AppMode
from app.proxmox_client import ProxmoxConnectionError
from unittest.mock import patch, AsyncMock


client = TestClient(app)

VALID_API_KEY = settings.api_key
AUTH_HEADERS = {"X-API-Key": VALID_API_KEY}
BEARER_HEADERS = {"Authorization": f"Bearer {VALID_API_KEY}"}


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
    assert data["version"] == "0.2.0"


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
            "Nem sikerült csatlakozni a Proxmox szerverhez (Kapcsolódási hiba).",
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

    # Visszaállítjuk DEMO módra
    settings.mode = AppMode.DEMO
