package hu.petermihalek.proxmonitor

import com.google.gson.Gson
import hu.petermihalek.proxmonitor.network.ApiService
import hu.petermihalek.proxmonitor.network.CpuInfo
import hu.petermihalek.proxmonitor.network.MemoryInfo
import hu.petermihalek.proxmonitor.network.ResourceItem
import hu.petermihalek.proxmonitor.network.ResourcesResponse
import hu.petermihalek.proxmonitor.network.RetrofitInstance
import hu.petermihalek.proxmonitor.network.ServerStatusResponse
import hu.petermihalek.proxmonitor.network.StorageInfo
import hu.petermihalek.proxmonitor.network.StoragePoolItem
import java.io.IOException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Egységtesztek a JSON-adatmodellek deszerializációjához, az URL-validációhoz,
 * valamint a MainViewModel sikeres (LIVE) és sikertelen állapotkezeléséhez.
 */
class ExampleUnitTest {

    private val gson = Gson()
    private val testScope = CoroutineScope(SupervisorJob() + Dispatchers.Unconfined)

    @Test
    fun serverStatusResponse_jsonDeserialization_parsesLiveResponseCorrectly() {
        val json = """
            {
              "mode": "LIVE",
              "node_name": "prox",
              "uptime_seconds": 1288800,
              "uptime_formatted": "14 nap, 22 óra, 0 perc",
              "cpu": {
                "usage_percent": 1.4,
                "cores": 12
              },
              "memory": {
                "used_bytes": 11596411699,
                "total_bytes": 16428249907,
                "formatted": "10.8 GB / 15.3 GB",
                "usage_percent": 70.6
              },
              "storage": {
                "used_bytes": 16941498368,
                "total_bytes": 72722055168,
                "formatted": "15.8 GB / 67.7 GB",
                "usage_percent": 23.3
              },
              "storage_pools": [
                {
                  "name": "local-lvm",
                  "type": "lvmthin",
                  "used_bytes": 158037017257,
                  "total_bytes": 168824930304,
                  "formatted": "147.2 GB / 157.2 GB",
                  "usage_percent": 93.6,
                  "content": "images,rootdir"
                }
              ]
            }
        """.trimIndent()

        val status = gson.fromJson(json, ServerStatusResponse::class.java)

        assertEquals("LIVE", status.mode)
        assertEquals("prox", status.node_name)
        assertEquals(1288800L, status.uptime_seconds)
        assertEquals(12, status.cpu.cores)
        assertEquals(1.4, status.cpu.usage_percent, 0.01)
        assertEquals("10.8 GB / 15.3 GB", status.memory.formatted)
        assertNotNull(status.storage_pools)
        assertEquals(1, status.storage_pools?.size)
        assertEquals("local-lvm", status.storage_pools?.first()?.name)
    }

    @Test
    fun resourcesResponse_jsonDeserialization_parsesVmAndLxcListCorrectly() {
        val json = """
            {
              "mode": "LIVE",
              "resources": [
                {
                  "vmid": 100,
                  "name": "haos",
                  "type": "VM",
                  "raw_type": "qemu",
                  "status": "running",
                  "display_status": "Online",
                  "cpu_percent": 3.2,
                  "memory_used_bytes": 2147483648,
                  "memory_formatted": "2.0 GB / 4.0 GB"
                },
                {
                  "vmid": 101,
                  "name": "jellyfin",
                  "type": "LXC",
                  "raw_type": "lxc",
                  "status": "stopped",
                  "display_status": "Offline",
                  "cpu_percent": 0.0,
                  "memory_used_bytes": 0,
                  "memory_formatted": "0 B / 8.0 GB"
                }
              ]
            }
        """.trimIndent()

        val response = gson.fromJson(json, ResourcesResponse::class.java)

        assertEquals("LIVE", response.mode)
        assertEquals(2, response.resources.size)
        assertEquals(100, response.resources[0].vmid)
        assertEquals("haos", response.resources[0].name)
        assertEquals("Online", response.resources[0].display_status)
        assertEquals("LXC", response.resources[1].type)
        assertEquals("Offline", response.resources[1].display_status)
    }

    @Test
    fun mainViewModel_liveModeSuccess_updatesUiStateToSuccess() {
        val fakeApi = object : ApiService {
            override suspend fun getServerStatus(apiKey: String): ServerStatusResponse {
                return ServerStatusResponse(
                    mode = "LIVE",
                    node_name = "prox",
                    uptime_seconds = 3600L,
                    uptime_formatted = "1 óra, 0 perc",
                    cpu = CpuInfo(usage_percent = 10.5, cores = 12),
                    memory = MemoryInfo(
                        used_bytes = 4000000000L,
                        total_bytes = 16000000000L,
                        formatted = "4.0 GB / 16.0 GB",
                        usage_percent = 25.0
                    ),
                    storage = StorageInfo(
                        used_bytes = 10000000000L,
                        total_bytes = 50000000000L,
                        formatted = "10.0 GB / 50.0 GB",
                        usage_percent = 20.0
                    ),
                    storage_pools = listOf(
                        StoragePoolItem(
                            name = "local",
                            type = "dir",
                            used_bytes = 10000000000L,
                            total_bytes = 50000000000L,
                            formatted = "10.0 GB / 50.0 GB",
                            usage_percent = 20.0
                        )
                    )
                )
            }

            override suspend fun getResources(apiKey: String): ResourcesResponse {
                return ResourcesResponse(
                    mode = "LIVE",
                    resources = listOf(
                        ResourceItem(
                            vmid = 100,
                            name = "haos",
                            type = "VM",
                            raw_type = "qemu",
                            status = "running",
                            display_status = "Online",
                            cpu_percent = 2.5,
                            memory_used_bytes = 2147483648L,
                            memory_formatted = "2.0 GB / 4.0 GB"
                        )
                    )
                )
            }
        }

        val viewModel = MainViewModel(
            apiProvider = { fakeApi },
            urlUpdater = { RetrofitInstance.normalizeBaseUrl(it) },
            customScope = testScope,
            autoLoad = true
        )

        assertEquals("", viewModel.apiKey)
        val state = viewModel.uiState.value
        assertTrue(state is UiState.Success)
        val success = state as UiState.Success
        assertEquals("LIVE", success.status.mode)
        assertEquals("prox", success.status.node_name)
        assertEquals(1, success.resources.size)
        assertEquals("haos", success.resources.first().name)
    }

    @Test
    fun mainViewModel_failedRequest_updatesUiStateToError() {
        val failingApi = object : ApiService {
            override suspend fun getServerStatus(apiKey: String): ServerStatusResponse {
                throw IOException("Kapcsolat elutasítva")
            }

            override suspend fun getResources(apiKey: String): ResourcesResponse {
                throw IOException("Kapcsolat elutasítva")
            }
        }

        val viewModel = MainViewModel(
            apiProvider = { failingApi },
            urlUpdater = { RetrofitInstance.normalizeBaseUrl(it) },
            customScope = testScope,
            autoLoad = true
        )

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertTrue((state as UiState.Error).message.contains("Hálózati hiba"))
    }

    @Test
    fun mainViewModel_invalidUrlInSettings_doesNotCrashAndSetsErrorState() {
        val dummyApi = object : ApiService {
            override suspend fun getServerStatus(apiKey: String): ServerStatusResponse {
                throw IOException("Nem hívódhat meg érvénytelen URL-nél")
            }

            override suspend fun getResources(apiKey: String): ResourcesResponse {
                throw IOException("Nem hívódhat meg érvénytelen URL-nél")
            }
        }

        val viewModel = MainViewModel(
            apiProvider = { dummyApi },
            urlUpdater = { RetrofitInstance.normalizeBaseUrl(it) },
            customScope = testScope,
            autoLoad = false
        )

        viewModel.updateSettings("   ", "teszt-kulcs")
        assertTrue(viewModel.uiState.value is UiState.Error)

        viewModel.updateSettings("http://hibas url szokozzel", "teszt-kulcs")
        assertTrue(viewModel.uiState.value is UiState.Error)
    }

    @Test
    fun retrofitInstance_normalizeBaseUrl_handlesLocalHttpAndRemoteHttps() {
        assertEquals("http://10.0.2.2:8000/", RetrofitInstance.normalizeBaseUrl("10.0.2.2:8000"))
        assertEquals("http://127.0.0.1:8000/", RetrofitInstance.normalizeBaseUrl("127.0.0.1:8000"))
        assertEquals("https://prox.example.com/", RetrofitInstance.normalizeBaseUrl("prox.example.com"))
    }
}
