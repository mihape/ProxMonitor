"""Proxmox VE REST API kliens a valós szerveradatok lekérdezéséhez."""

from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.models import (
    CpuStatus,
    MemoryStatus,
    StorageStatus,
    ServerStatusResponse,
    ResourceItem,
    ResourcesResponse,
)


class ProxmoxConnectionError(Exception):
    """Kivétel, ha a Proxmox VE szerver nem érhető el vagy hibát jelez."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _format_bytes(bytes_value: int) -> str:
    """Bájtok ember által könnyen olvasható formázása (GB / TB)."""
    if bytes_value >= 1024 ** 4:
        return f"{bytes_value / (1024 ** 4):.1f} TB"
    elif bytes_value >= 1024 ** 3:
        return f"{bytes_value / (1024 ** 3):.1f} GB"
    elif bytes_value >= 1024 ** 2:
        return f"{bytes_value / (1024 ** 2):.1f} MB"
    return f"{bytes_value} B"


def _format_uptime(seconds: int) -> str:
    """Üzemidő másodpercekből nap, óra, perc formátumba konvertálása."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days} nap, {hours} óra, {minutes} perc"
    elif hours > 0:
        return f"{hours} óra, {minutes} perc"
    return f"{minutes} perc"


class ProxmoxClient:
    """Aszinkron HTTP kliens a Proxmox VE REST API-hoz."""

    def __init__(self) -> None:
        self.host = settings.proxmox_host.rstrip("/") if settings.proxmox_host else ""
        self.node = settings.proxmox_node or "pve"
        self.token_id = settings.proxmox_token_id or ""
        self.token_secret = settings.proxmox_token_secret or ""

    def _get_client_kwargs(self) -> Dict[str, Any]:
        """Összeállítja a httpx.AsyncClient paramétereit (SSL, Timeout, Fejlécek)."""
        headers = {
            "Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}",
            "Accept": "application/json",
        }

        # SSL hitelesítés kezelése
        if settings.proxmox_ca_cert:
            ssl_verify: Any = settings.proxmox_ca_cert
        else:
            ssl_verify = settings.proxmox_verify_ssl

        return {
            "headers": headers,
            "verify": ssl_verify,
            "timeout": httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
        }

    async def get_node_status(self) -> ServerStatusResponse:
        """
        Lekérdezi a node állapotát a Proxmox '/api2/json/nodes/{node}/status' végpontjáról.
        """
        url = f"{self.host}/api2/json/nodes/{self.node}/status"

        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.get(url)
        except httpx.ConnectError as e:
            raise ProxmoxConnectionError(
                f"Nem sikerült csatlakozni a Proxmox szerverhez ({self.host}): Kapcsolódási hiba ({e}).",
                status_code=502,
            )
        except httpx.TimeoutException:
            raise ProxmoxConnectionError(
                f"Időtúllépés a Proxmox szerver elérésekor ({self.host}).",
                status_code=504,
            )
        except Exception as e:
            raise ProxmoxConnectionError(
                f"Hálózati hiba a Proxmox kommunikáció során: {e}",
                status_code=502,
            )

        if response.status_code == 401 or response.status_code == 403:
            raise ProxmoxConnectionError(
                "Proxmox hitelesítési hiba: Érvénytelen API token (PVEAPIToken). Ellenőrizd a PROXMOX_TOKEN_ID és PROXMOX_TOKEN_SECRET értékeket!",
                status_code=502,
            )
        elif response.status_code != 200:
            raise ProxmoxConnectionError(
                f"A Proxmox szerver hibakódot adott: HTTP {response.status_code} ({response.text})",
                status_code=502,
            )

        data = response.json().get("data", {})

        # CPU adatok
        raw_cpu = data.get("cpu", 0.0)
        cpu_percent = round(float(raw_cpu) * 100.0, 1)
        cpu_cores = data.get("cpuinfo", {}).get("cpus", 1)

        # Memória adatok
        mem_info = data.get("memory", {})
        mem_used = int(mem_info.get("used", 0))
        mem_total = int(mem_info.get("total", 1))
        mem_percent = round((mem_used / mem_total) * 100.0, 1) if mem_total > 0 else 0.0
        mem_formatted = f"{_format_bytes(mem_used)} / {_format_bytes(mem_total)}"

        # Háttértár adatok (rootfs)
        rootfs_info = data.get("rootfs", {})
        disk_used = int(rootfs_info.get("used", 0))
        disk_total = int(rootfs_info.get("total", 1))
        disk_percent = round((disk_used / disk_total) * 100.0, 1) if disk_total > 0 else 0.0
        disk_formatted = f"{_format_bytes(disk_used)} / {_format_bytes(disk_total)}"

        # Üzemidő
        uptime_sec = int(data.get("uptime", 0))

        return ServerStatusResponse(
            mode="LIVE",
            node_name=self.node,
            uptime_seconds=uptime_sec,
            uptime_formatted=_format_uptime(uptime_sec),
            cpu=CpuStatus(
                usage_percent=cpu_percent,
                cores=cpu_cores,
            ),
            memory=MemoryStatus(
                used_bytes=mem_used,
                total_bytes=mem_total,
                formatted=mem_formatted,
                usage_percent=mem_percent,
            ),
            storage=StorageStatus(
                used_bytes=disk_used,
                total_bytes=disk_total,
                formatted=disk_formatted,
                usage_percent=disk_percent,
            ),
        )

    async def get_cluster_resources(self) -> ResourcesResponse:
        """
        Lekérdezi a virtuális gépeket és konténereket a '/api2/json/cluster/resources?type=vm' végpontról.
        """
        url = f"{self.host}/api2/json/cluster/resources?type=vm"

        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.get(url)
        except httpx.ConnectError as e:
            raise ProxmoxConnectionError(
                f"Nem sikerült csatlakozni a Proxmox szerverhez ({self.host}): Kapcsolódási hiba ({e}).",
                status_code=502,
            )
        except httpx.TimeoutException:
            raise ProxmoxConnectionError(
                f"Időtúllépés a Proxmox szerver elérésekor ({self.host}).",
                status_code=504,
            )
        except Exception as e:
            raise ProxmoxConnectionError(
                f"Hálózati hiba a Proxmox kommunikáció során: {e}",
                status_code=502,
            )

        if response.status_code != 200:
            raise ProxmoxConnectionError(
                f"A Proxmox szerver hibakódot adott a cluster/resources hívásra: HTTP {response.status_code}",
                status_code=502,
            )

        items_data = response.json().get("data", [])
        resources_list: List[ResourceItem] = []

        for item in items_data:
            raw_type = item.get("type", "qemu")
            display_type = "VM" if raw_type == "qemu" else "LXC"
            raw_status = item.get("status", "unknown")
            display_status = "Online" if raw_status == "running" else "Offline"

            cpu_val = round(float(item.get("cpu", 0.0)) * 100.0, 1)
            mem_used = int(item.get("mem", 0))
            max_mem = int(item.get("maxmem", 0))
            mem_formatted = f"{_format_bytes(mem_used)} / {_format_bytes(max_mem)}" if max_mem > 0 else _format_bytes(mem_used)

            resources_list.append(
                ResourceItem(
                    vmid=int(item.get("vmid", 0)),
                    name=item.get("name", f"VM {item.get('vmid')}"),
                    type=display_type,
                    raw_type=raw_type,
                    status=raw_status,
                    display_status=display_status,
                    cpu_percent=cpu_val,
                    memory_used_bytes=mem_used,
                    memory_formatted=mem_formatted,
                )
            )

        # VMID szerint rendezve
        resources_list.sort(key=lambda r: r.vmid)

        return ResourcesResponse(
            mode="LIVE",
            resources=resources_list,
        )
