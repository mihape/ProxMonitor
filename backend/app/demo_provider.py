"""Mintaadat-szolgáltató (DEMO mód) a fejlesztéshez és Proxmox nélküli bemutatóhoz."""

from app.models import (
    CpuStatus,
    MemoryStatus,
    StorageStatus,
    ServerStatusResponse,
    ResourceItem,
    ResourcesResponse,
)


def get_demo_server_status() -> ServerStatusResponse:
    """Visszaadja a statikus mintaadatokat a szerver állapotáról."""
    return ServerStatusResponse(
        mode="DEMO",
        node_name="pve-demo-node",
        uptime_seconds=1284520,
        uptime_formatted="14 nap, 20 óra, 48 perc",
        cpu=CpuStatus(
            usage_percent=24.0,
            cores=8,
        ),
        memory=MemoryStatus(
            used_bytes=8804682956,
            total_bytes=17179869184,
            formatted="8.2 GB / 16 GB",
            usage_percent=51.2,
        ),
        storage=StorageStatus(
            used_bytes=1979120929996,
            total_bytes=4398046511104,
            formatted="1.8 TB / 4 TB",
            usage_percent=45.0,
        ),
    )


def get_demo_resources() -> ResourcesResponse:
    """Visszaadja a virtuális gépek és konténerek mintaadatait."""
    return ResourcesResponse(
        mode="DEMO",
        resources=[
            ResourceItem(
                vmid=100,
                name="Home Assistant",
                type="VM",
                raw_type="qemu",
                status="running",
                display_status="Online",
                cpu_percent=3.2,
                memory_used_bytes=2147483648,
                memory_formatted="2.0 GB / 4.0 GB",
            ),
            ResourceItem(
                vmid=101,
                name="Jellyfin",
                type="LXC",
                raw_type="lxc",
                status="running",
                display_status="Online",
                cpu_percent=12.5,
                memory_used_bytes=4294967296,
                memory_formatted="4.0 GB / 8.0 GB",
            ),
            ResourceItem(
                vmid=102,
                name="AdGuard Home",
                type="LXC",
                raw_type="lxc",
                status="running",
                display_status="Online",
                cpu_percent=0.8,
                memory_used_bytes=536870912,
                memory_formatted="512 MB / 1.0 GB",
            ),
        ],
    )
