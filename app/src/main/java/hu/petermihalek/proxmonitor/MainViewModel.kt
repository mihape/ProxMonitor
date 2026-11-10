package hu.petermihalek.proxmonitor

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import hu.petermihalek.proxmonitor.network.ApiService
import hu.petermihalek.proxmonitor.network.ResourceItem
import hu.petermihalek.proxmonitor.network.RetrofitInstance
import hu.petermihalek.proxmonitor.network.ServerStatusResponse
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

sealed interface UiState {
    object Loading : UiState
    data class Success(
        val status: ServerStatusResponse,
        val resources: List<ResourceItem>
    ) : UiState
    data class Error(val message: String) : UiState
}

class MainViewModel(
    private val apiProvider: () -> ApiService,
    private val urlUpdater: (String) -> String,
    private val customScope: CoroutineScope?,
    autoLoad: Boolean = true
) : ViewModel() {

    constructor() : this(
        apiProvider = { RetrofitInstance.getApi() },
        urlUpdater = { RetrofitInstance.updateBaseUrl(it) },
        customScope = null,
        autoLoad = true
    )

    private val activeScope: CoroutineScope
        get() = customScope ?: viewModelScope

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    // Korábbi futó lekérdezés megszakítása a versenyhelyzetek (race condition) elkerülésére
    private var loadJob: Job? = null

    var serverUrl: String = RetrofitInstance.baseUrl
        private set

    var apiKey: String = ""
        private set

    init {
        if (autoLoad) {
            loadData()
        }
    }

    fun updateSettings(newUrl: String, newApiKey: String) {
        loadJob?.cancel()
        serverUrl = newUrl.trim()
        apiKey = newApiKey.trim()
        loadData()
    }

    fun loadData() {
        loadJob?.cancel()
        val targetUrl = serverUrl
        val targetApiKey = apiKey

        _uiState.value = UiState.Loading
        loadJob = activeScope.launch {
            try {
                val normalizedUrl = urlUpdater(targetUrl)
                serverUrl = normalizedUrl

                val api = apiProvider()
                val status = api.getServerStatus(targetApiKey)
                val resources = api.getResources(targetApiKey)
                ensureActive()
                _uiState.value = UiState.Success(status, resources.resources)
            } catch (e: CancellationException) {
                throw e
            } catch (e: IllegalArgumentException) {
                _uiState.value = UiState.Error(
                    "Érvénytelen kapcsolati beállítás: ${e.message ?: "Hibás szerver URL."}\n\n" +
                    "Kérlek, ellenőrizd a megadott címet a Beállításokban (⚙)!"
                )
            } catch (e: Exception) {
                _uiState.value = UiState.Error(
                    "Hálózati hiba: ${e.localizedMessage ?: e.message}\n\n" +
                    "Ellenőrizd a szerver elérhetőségét és az API kulcsot a Beállításokban (⚙):\n$targetUrl"
                )
            }
        }
    }
}
