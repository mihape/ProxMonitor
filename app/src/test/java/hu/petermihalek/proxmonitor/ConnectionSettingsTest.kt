package hu.petermihalek.proxmonitor

import hu.petermihalek.proxmonitor.network.ApiService
import hu.petermihalek.proxmonitor.network.ResourcesResponse
import hu.petermihalek.proxmonitor.network.RetrofitInstance
import hu.petermihalek.proxmonitor.network.ServerStatusResponse
import java.io.IOException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import org.junit.Assert.assertEquals
import org.junit.Test

class ConnectionSettingsTest {
    @Test
    fun savedSettings_areRestoredWhenViewModelIsRecreated() {
        var persisted = ConnectionSettings("http://10.0.2.2:8000/", "")
        val repository = object : ConnectionSettingsRepository {
            override fun read() = persisted
            override fun write(settings: ConnectionSettings) { persisted = settings }
        }
        val fakeApi = object : ApiService {
            override suspend fun getServerStatus(apiKey: String): ServerStatusResponse =
                throw IOException("offline")
            override suspend fun getResources(apiKey: String): ResourcesResponse =
                throw IOException("offline")
        }
        val testScope = CoroutineScope(SupervisorJob() + Dispatchers.Unconfined)
        fun newModel() = MainViewModel(
            apiProvider = { fakeApi },
            urlUpdater = { RetrofitInstance.normalizeBaseUrl(it) },
            customScope = testScope,
            autoLoad = false,
            settingsRepository = repository
        )

        newModel().updateSettings("prox.example.com", "test-api-key")
        val recreated = newModel()
        assertEquals("https://prox.example.com/", recreated.serverUrl)
        assertEquals("test-api-key", recreated.apiKey)
    }
}
