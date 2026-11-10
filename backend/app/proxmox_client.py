import logging
from typing import Any, Dict, List
import httpx
from app.config import settings
from app.models import (
    CpuStatus,
    MemoryStatus,
    ResourceItem,
    ResourcesResponse,
    ServerStatusResponse,
    StoragePoolItem,
    StorageStatus,
)

logger = logging.getLogger(__name__)


class ProxmoxConnectionError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _format_bytes(bytes_value: int) -> str:
    if bytes_value >= 1024 ** 4:
        return f"{bytes_value / (1024 ** 4):.1f} TB"
    elif bytes_value >= 1024 ** 3:
        return f"{bytes_value / (1024 ** 3):.1f} GB"
    elif bytes_value >= 1024 ** 2:
        return f"{bytes_value / (1024 ** 2):.1f} MB"
    return f"{bytes_value} B"


def _format_uptime(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days} nap, {hours} óra, {minutes} perc"
    elif hours > 0:
        return f"{hours} óra, {minutes} perc"
    return f"{minutes} perc"


class ProxmoxClient:
    """Aszinkron HTTP-kliens a Proxmox VE REST API (`PVEAPIToken`) eléréséhez."""

    def __init__(self) -> None:
        self.host = settings.proxmox_host.rstrip("/") if settings.proxmox_host else ""
        self.node = settings.proxmox_node or "pve"
        self.token_id = settings.proxmox_token_id or ""
        self.token_secret = settings.proxmox_token_secret or ""

    def _get_client_kwargs(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}",
            "Accept": "application/json",
        }

        if settings.proxmox_ca_cert:
            ssl_verify: Any = settings.proxmox_ca_cert
        else:
            ssl_verify = settings.proxmox_verify_ssl

        return {
            "headers": headers,
            "verify": ssl_verify,
            "timeout": httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
        }

    async def _get_available_nodes(self, client: httpx.AsyncClient) -> List[str]:
        try:
            resp = await client.get(f"{self.host}/api2/json/nodes")
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return [item.get("node") for item in data if item.get("node")]
        except Exception:
            pass
        return []

    async def get_node_status(self) -> ServerStatusResponse:
        """Csomópont állapotának lekérdezése; eltérő node-név esetén egycsomópontos automatikus felderítéssel."""
        url = f"{self.host}/api2/json/nodes/{self.node}/status"

        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    available = await self._get_available_nodes(client)
                    if available and self.node not in available:
                        # Egynode-os Proxmox környezetben automatikus átállás az egyetlen elérhető csomópontra
                        if len(available) == 1:
                            actual_node = available[0]
                            retry_resp = await client.get(f"{self.host}/api2/json/nodes/{actual_node}/status")
                            if retry_resp.status_code == 200:
                                self.node = actual_node
                                response = retry_resp

                        if response.status_code != 200:
                            logger.error(
                                "A(z) '%s' csomópont nem található (%s). Elérhető csomópontok: %s",
                                self.node,
                                self.host,
                                ", ".join(available),
                            )
                            raise ProxmoxConnectionError(
                                "A megadott Proxmox csomópont nem található a szerveren.",
                                status_code=502,
                            )
        except httpx.ConnectError as e:
            logger.error("Proxmox kapcsolódási hiba (%s): %s", self.host, e)
            raise ProxmoxConnectionError(
                "Nem sikerült csatlakozni a Proxmox szerverhez.",
                status_code=502,
            )
        except httpx.TimeoutException as e:
            logger.error("Proxmox időtúllépés (%s): %s", self.host, e)
            raise ProxmoxConnectionError(
                "Időtúllépés a Proxmox szerver elérésekor.",
                status_code=504,
            )
        except ProxmoxConnectionError:
            raise
        except Exception as e:
            logger.error("Hálózati hiba a Proxmox kommunikáció során (%s): %s", self.host, e)
            raise ProxmoxConnectionError(
                "Hálózati hiba történt a Proxmox kommunikáció során.",
                status_code=502,
            )

        if response.status_code == 401 or response.status_code == 403:
            logger.error("Proxmox hitelesítési hiba (%s): HTTP %s", self.host, response.status_code)
            raise ProxmoxConnectionError(
                "A Proxmox szerver elutasította a hitelesítést.",
                status_code=502,
            )
        elif response.status_code != 200:
            logger.error(
                "Proxmox HTTP hiba a node status lekérésekor (%s): HTTP %s (%s)",
                self.host,
                response.status_code,
                response.text,
            )
            raise ProxmoxConnectionError(
                "A Proxmox szerver hibát jelzett az állapot lekérdezésekor.",
                status_code=502,
            )

        data = response.json().get("data", {})

        raw_cpu = data.get("cpu", 0.0)
        cpu_percent = round(float(raw_cpu) * 100.0, 1)
        cpu_cores = data.get("cpuinfo", {}).get("cpus", 1)

        mem_info = data.get("memory", {})
        mem_used = int(mem_info.get("used", 0))
        mem_total = int(mem_info.get("total", 1))
        mem_percent = round((mem_used / mem_total) * 100.0, 1) if mem_total > 0 else 0.0
        mem_formatted = f"{_format_bytes(mem_used)} / {_format_bytes(mem_total)}"

        rootfs_info = data.get("rootfs", {})
        disk_used = int(rootfs_info.get("used", 0))
        disk_total = int(rootfs_info.get("total", 1))
        disk_percent = round((disk_used / disk_total) * 100.0, 1) if disk_total > 0 else 0.0
        disk_formatted = f"{_format_bytes(disk_used)} / {_format_bytes(disk_total)}"

        uptime_sec = int(data.get("uptime", 0))

        storage_pools: List[StoragePoolItem] = []
        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                st_resp = await client.get(f"{self.host}/api2/json/nodes/{self.node}/storage")
                if st_resp.status_code == 200:
                    st_data = st_resp.json().get("data", [])
                    for item in st_data:
                        # Csak az aktív és engedélyezett tárolók szerepelnek a kimutatásban
                        if item.get("enabled", 1) == 1 and item.get("active", 1) == 1:
                            s_name = item.get("storage", "")
                            s_type = item.get("type", "dir")
                            s_used = int(item.get("used", 0))
                            s_total = int(item.get("total", 0))
                            s_content = item.get("content", "")
                            s_percent = round((s_used / s_total) * 100.0, 1) if s_total > 0 else 0.0
                            s_fmt = f"{_format_bytes(s_used)} / {_format_bytes(s_total)}" if s_total > 0 else "0 B"

                            storage_pools.append(
                                StoragePoolItem(
                                    name=s_name,
                                    type=s_type,
                                    used_bytes=s_used,
                                    total_bytes=s_total,
                                    formatted=s_fmt,
                                    usage_percent=s_percent,
                                    content=s_content,
                                )
                            )
        except Exception:
            # Részletes tárolólekérdezés hibája esetén a gyökérpartíció (rootfs) adatai elegendőek
            pass

        storage_pools.sort(key=lambda s: s.name)

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
            storage_pools=storage_pools,
        )

    async def get_cluster_resources(self) -> ResourcesResponse:
        url = f"{self.host}/api2/json/cluster/resources?type=vm"

        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.get(url)
        except httpx.ConnectError as e:
            logger.error("Proxmox kapcsolódási hiba (%s): %s", self.host, e)
            raise ProxmoxConnectionError(
                "Nem sikerült csatlakozni a Proxmox szerverhez.",
                status_code=502,
            )
        except httpx.TimeoutException as e:
            logger.error("Proxmox időtúllépés (%s): %s", self.host, e)
            raise ProxmoxConnectionError(
                "Időtúllépés a Proxmox szerver elérésekor.",
                status_code=504,
            )
        except Exception as e:
            logger.error("Hálózati hiba a Proxmox kommunikáció során (%s): %s", self.host, e)
            raise ProxmoxConnectionError(
                "Hálózati hiba történt a Proxmox kommunikáció során.",
                status_code=502,
            )

        if response.status_code == 401 or response.status_code == 403:
            logger.error("Proxmox hitelesítési hiba (%s): HTTP %s", self.host, response.status_code)
            raise ProxmoxConnectionError(
                "A Proxmox szerver elutasította a hitelesítést.",
                status_code=502,
            )
        elif response.status_code != 200:
            logger.error(
                "Proxmox HTTP hiba az erőforrások lekérésekor (%s): HTTP %s (%s)",
                self.host,
                response.status_code,
                response.text,
            )
            raise ProxmoxConnectionError(
                "A Proxmox szerver hibát jelzett az erőforrások lekérdezésekor.",
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

        resources_list.sort(key=lambda r: r.vmid)

        return ResourcesResponse(
            mode="LIVE",
            resources=resources_list,
        )
