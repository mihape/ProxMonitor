package hu.petermihalek.proxmonitor.network

data class ServerStatusResponse(
    val mode: String,
    val node_name: String,
    val uptime_seconds: Long,
    val uptime_formatted: String,
    val cpu: CpuInfo,
    val memory: MemoryInfo,
    val storage: StorageInfo,
    val storage_pools: List<StoragePoolItem>? = null
)

data class StoragePoolItem(
    val name: String,
    val type: String,
    val used_bytes: Long,
    val total_bytes: Long,
    val formatted: String,
    val usage_percent: Double,
    val content: String? = null
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
