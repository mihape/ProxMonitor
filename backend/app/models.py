"""Pydantic adatmodellek a REST API kérésekhez és válaszokhoz."""

from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """A /health végpont válaszmodellje."""
    status: str = Field(default="online", description="A szolgáltatás állapota")
    application: str = Field(default="ProxMonitor", description="Alkalmazás neve")
    version: str = Field(default="0.2.0", description="Backend verzió")


class CpuStatus(BaseModel):
    """CPU terhelési adatok."""
    usage_percent: float = Field(..., ge=0.0, le=100.0, description="Processzor terheltség százalékban")
    cores: int = Field(default=1, ge=1, description="Elérhető processzormagok száma")


class MemoryStatus(BaseModel):
    """Memóriahasználati adatok."""
    used_bytes: int = Field(..., ge=0, description="Felhasznált RAM bájtban")
    total_bytes: int = Field(..., ge=0, description="Összes RAM bájtban")
    formatted: str = Field(..., description="Ember által olvasható formátum (pl. 8.2 GB / 16 GB)")
    usage_percent: float = Field(..., ge=0.0, le=100.0, description="Memóriahasználat százalékban")


class StorageStatus(BaseModel):
    """Háttértár-használati adatok (összesített vagy gyökér)."""
    used_bytes: int = Field(..., ge=0, description="Felhasznált lemezterület bájtban")
    total_bytes: int = Field(..., ge=0, description="Összes lemezterület bájtban")
    formatted: str = Field(..., description="Ember által olvasható formátum (pl. 1.8 TB / 4 TB)")
    usage_percent: float = Field(..., ge=0.0, le=100.0, description="Tárhelyhasználat százalékban")


class StoragePoolItem(BaseModel):
    """Egyedi háttértár (pl. SSD gyökér, LVM tároló, 4TB HDD, NAS)."""
    name: str = Field(..., description="Tárhely azonosítója (pl. local, local-lvm, torrent)")
    type: str = Field(default="dir", description="Tárhely típusa (pl. dir, lvmthin, nfs, cifs)")
    used_bytes: int = Field(default=0, ge=0, description="Felhasznált lemezterület bájtban")
    total_bytes: int = Field(default=0, ge=0, description="Összes kapacitás bájtban")
    formatted: str = Field(..., description="Formázott méret (pl. 3.1 TB / 3.7 TB)")
    usage_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Kihasználtság százalékban")
    content: Optional[str] = Field(default="", description="Tárolt tartalomtípusok")


class ServerStatusResponse(BaseModel):
    """A /api/v1/status végpont válaszmodellje."""
    mode: str = Field(..., description="Adatforrás mód: DEMO vagy LIVE")
    node_name: str = Field(..., description="A Proxmox csomópont (node) neve")
    uptime_seconds: int = Field(..., ge=0, description="Szerver üzemidő másodpercben")
    uptime_formatted: str = Field(..., description="Üzemidő formázva (pl. 14 nap, 20 óra)")
    cpu: CpuStatus = Field(..., description="CPU statisztikák")
    memory: MemoryStatus = Field(..., description="Memória statisztikák")
    storage: StorageStatus = Field(..., description="Tárhely statisztikák")
    storage_pools: List[StoragePoolItem] = Field(default_factory=list, description="Részletes tárolók listája (SSD, HDD, NAS)")


class ResourceItem(BaseModel):
    """Egy virtuális gép (VM) vagy konténer (LXC) adatai."""
    vmid: int = Field(..., description="Egyedi Proxmox VMID")
    name: str = Field(..., description="Virtuális gép vagy konténer neve")
    type: str = Field(..., description="Típus megjelenítéshez: VM vagy LXC")
    raw_type: str = Field(..., description="Proxmox típus: qemu vagy lxc")
    status: str = Field(..., description="Futási állapot: running vagy stopped")
    display_status: str = Field(..., description="Magyar/felhasználóbarát státusz: Online / Offline")
    cpu_percent: float = Field(default=0.0, ge=0.0, description="Pillanatnyi CPU használat százalékban")
    memory_used_bytes: int = Field(default=0, ge=0, description="Felhasznált RAM bájtban")
    memory_formatted: str = Field(default="", description="Formázott memóriahasználat")


class ResourcesResponse(BaseModel):
    """A /api/v1/resources végpont válaszmodellje."""
    mode: str = Field(..., description="Adatforrás mód: DEMO vagy LIVE")
    resources: List[ResourceItem] = Field(..., description="Virtuális gépek és konténerek listája")
