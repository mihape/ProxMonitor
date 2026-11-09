package hu.petermihalek.proxmonitor

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import hu.petermihalek.proxmonitor.network.ResourceItem
import hu.petermihalek.proxmonitor.network.RetrofitInstance
import hu.petermihalek.proxmonitor.network.ServerStatusResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

/**
 * A képernyő lehetséges állapotai (Sealed interface):
 * - Loading: Adatok lekérdezése folyamatban van (töltésjelző).
 * - Success: Sikeres válasz mindkét végpontról (megjeleníthető adatok).
 * - Error: Hálózati vagy szerverhiba (hibaüzenet + újrapróbálkozás).
 */
sealed interface UiState {
    object Loading : UiState
    data class Success(
        val status: ServerStatusResponse,
        val resources: List<ResourceItem>
    ) : UiState
    data class Error(val message: String) : UiState
}

/**
 * A főképernyő ViewModel-je (MVVM architektúra).
 * Felelős az adatok aszinkron lekéréséért Coroutine-ok segítségével,
 * valamint az állapot (UiState) életciklus-biztos megőrzéséért.
 */
class MainViewModel : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    // Alapértelmezett beállítások (Emulátor és az aktuális konfigurált API kulcs)
    var serverUrl: String = RetrofitInstance.baseUrl
        private set

    var apiKey: String = "petipe@1"
        private set

    init {
        loadData()
    }

    /**
     * Beállítások (szervercím és kulcs) frissítése, majd adatok újratöltése.
     */
    fun updateSettings(newUrl: String, newApiKey: String) {
        serverUrl = newUrl
        apiKey = newApiKey
        RetrofitInstance.updateBaseUrl(newUrl)
        loadData()
    }

    /**
     * Lekéri a szerver állapotát és az erőforrások listáját a háttérben.
     */
    fun loadData() {
        _uiState.value = UiState.Loading
        viewModelScope.launch {
            try {
                val api = RetrofitInstance.getApi()
                val status = api.getServerStatus(apiKey)
                val resources = api.getResources(apiKey)
                _uiState.value = UiState.Success(status, resources.resources)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(
                    "Hálózati hiba: ${e.localizedMessage ?: e.message}\n\n" +
                    "Ellenőrizd, hogy elindítottad-e a Python backendet a gépen:\n$serverUrl"
                )
            }
        }
    }
}
