package hu.petermihalek.proxmonitor.network

/**
 * A Proxmox szerver általános állapotának adatmodellje.
 * A backend GET /api/v1/status végpontjának JSON válaszát képezi le.
 */
data class ServerStatusResponse(
    val mode: String,
    val node_name: String,
    val uptime_seconds: Long,
    val uptime_formatted: String,
    val cpu: CpuInfo,
    val memory: MemoryInfo,
    val storage: StorageInfo
)

data class CpuInfo(
    val usage_percent: Double,
    val cores: Int
)

data class MemoryInfo(
    val used_bytes: Long,
    val total_bytes: Long,
    val formatted: String,
    val usage_percent: Double
)

data class StorageInfo(
    val used_bytes: Long,
    val total_bytes: Long,
    val formatted: String,
    val usage_percent: Double
)

/**
 * A virtuális gépek és konténerek listájának adatmodellje.
 * A backend GET /api/v1/resources végpontjának JSON válaszát képezi le.
 */
data class ResourcesResponse(
    val mode: String,
    val resources: List<ResourceItem>
)

data class ResourceItem(
    val vmid: Int,
    val name: String,
    val type: String,
    val raw_type: String,
    val status: String,
    val display_status: String,
    val cpu_percent: Double,
    val memory_used_bytes: Long,
    val memory_formatted: String
)
