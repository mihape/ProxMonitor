# Szakmai Beadandó Dolgozat

> **Intézmény:** Miskolci Egyetem – Gépészmérnöki és Informatikai Kar  
> **Képzés:** Felsőoktatási szakképzés (FOSZ)  
> **Tantárgy:** Mobilprogramozás  
> **Témakör:** REST API és JSON-feldolgozás Android-alkalmazásokban  
> **Projekt címe:** ProxMonitor – Proxmox VE infrastruktúra-felügyelet natív Android környezetben  
> **Verzió:** v1.0.0  
> **Készítette:** Mihalek Péter  

---

## 1. Bevezetés és a választott téma indoklása

A modern mobilalkalmazások működésének alapköve a hálózati kommunikáció. Napjainkban a szoftverrendszerek túlnyomó többsége elosztott architektúrát követ: a mobiltelefon vékony kliensként (Frontend) jeleníti meg az adatokat, míg a komplex üzleti logikát és adatbázis-műveleteket háttérkiszolgálók (Backend) végzik.

A kliens és a szerver közötti kapcsolattartás de facto iparági szabványa a **REST (Representational State Transfer)** architektúra, míg az adatok átvitelére és szerializálására a könnyen olvasható és platformfüggetlen **JSON (JavaScript Object Notation)** formátum szolgál.

A dolgozat és a hozzá tartozó **ProxMonitor** projekt célja a RESTful API-k Android környezetben történő professzionális kezelésének, az aszinkron hálózati műveleteknek és a strukturált JSON adatok deszerializációjának gyakorlati bemutatása egy valós idejű rendszermonitorozó alkalmazás megvalósításán keresztül.

---

## 2. A megoldott probléma: Proxmox VE infrastruktúra-felügyelet

A **Proxmox Virtual Environment (PVE)** egy nyílt forráskódú, vállalati szintű szerver-virtualizációs platform. Bár a Proxmox fejlett webes kezelőfelülettel rendelkezik, az asztali böngészőre tervezett felület okostelefonon nehezen kezelhető, lassú és nem nyújt azonnali, áttekinthető képet a szerver állapotáról.

A kifejlesztett **ProxMonitor** rendszer lehetővé teszi, hogy a szerverüzemeltető:
- másodpercek alatt ellenőrizhesse a szerver pillanatnyi processzor-, memória- és háttértár-terhelését (beleértve az egyes storage poolokat),
- nyomon kövesse a virtuális gépek (QEMU VM) és konténerek (LXC) futási állapotát,
- biztonságos csatornán keresztül, a legkisebb jogosultság elve mellett férjen hozzá a statisztikákhoz.

---

## 3. Rendszerarchitektúra és komponensek kapcsolata

A rendszer háromrétegű kliens-szerver architektúrára épül. A tesztelt környezetben a köztes FastAPI backend egy **Windows-laptopon** fut (`127.0.0.1:8000`), amelyet a fizikai Android telefon **Tailscale-en keresztül HTTPS-en** (Android emulátor esetén pedig a `http://10.0.2.2:8000/` címen) ér el:

```text
┌─────────────────────────────────┐
│       ANDROID MOBIL KLIENS      │
│  - Jetpack Compose & Material 3 │
│  - MainViewModel & UiState      │
│  - Retrofit 2 & Gson konverter  │
└────────────────┬────────────────┘
                 │ HTTPS (Tailscale) / HTTP (Emulátor: 10.0.2.2)
                 │ Fejléc: X-API-Key: <kulcs>
                 ▼
┌─────────────────────────────────┐
│  KÖZTES BACKEND (Windows-laptop)│
│  - Python 3 + FastAPI           │
│  - Pydantic v2 adatmodellek     │
│  - Proxmox API Token védelem    │
└────────────────┬────────────────┘
                 │ HTTPS / REST (PVE API)
                 │ Fejléc: PVEAPIToken=USER@REALM!TOKEN=UUID
                 ▼
┌─────────────────────────────────┐
│       PROXMOX VE HYPERVISOR     │
│  - Fizikai gazdagép ('prox')    │
│  - 19 db QEMU VM és LXC konténer│
└─────────────────────────────────┘
```

### Miért szükséges a köztes backend réteg?
A közvetlen telefon-szerver kapcsolat elkerülésének két kiemelt szakmai indoka van:
1. **Biztonság (Hitelesítő adatok védelme):**  
   A Proxmox API token korlátlan hozzáférést biztosíthat a teljes virtualizációs környezethez. Egy Android APK fájl könnyen visszafejthető (dekompilálható), így az alkalmazáskódban tilos érzékeny API-kulcsokat vagy jelszavakat tárolni. A köztes Python backend elrejti a Proxmox hitelesítést (`.env`), és a telefon felé egy szigorúan korlátozott, dedikált API-kulcsot (`X-API-Key`) kér.
2. **Hálózati terhelés és adatminimalizálás:**  
   A Proxmox natív API válaszai több száz technikai paramétert tartalmaznak. A mobilhálózat sávszélességének és akkumulátorának kímélése érdekében a FastAPI backend előfeldolgozza az adatokat, és kizárólag a telefonos felülethez szükséges lényeges mezőket továbbítja tiszta JSON formátumban.

---

## 4. Az Android kliens megvalósítása

### 4.1. Hálózati réteg: Retrofit 2, Gson és HTTPS biztonság
Az alkalmazás hálózatkezelése a Square által kifejlesztett **Retrofit 2** könyvtárra épül. A Retrofit deklaratív módon működik: a végpontokat egy Kotlin interfészben (`ApiService.kt`) definiáljuk:

```kotlin
interface ApiService {
    @GET("api/v1/status")
    suspend fun getServerStatus(
        @Header("X-API-Key") apiKey: String
    ): ServerStatusResponse

    @GET("api/v1/resources")
    suspend fun getResources(
        @Header("X-API-Key") apiKey: String
    ): ResourcesResponse
}
```

A `RetrofitInstance` gondoskodik a felhasználó által megadott szervercím validálásáról és normalizálásáról (`normalizeBaseUrl`): helyi fejlesztői címeknél (`10.0.2.2`, `127.0.0.1`, `localhost`) `http://`, minden egyéb távoli (pl. Tailscale) címnél biztonságos `https://` protokollt állít be, összhangban az alkalmazás `network_security_config.xml` szabályaival.

A válaszok deszerializációját a **Gson Converter** végzi. A beérkező szöveges JSON adatokat típusbiztos Kotlin adatosztályokká (`data class`) konvertálja:
```kotlin
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
```

### 4.2. Aszinkron működés és MVVM architektúra
Az Android rendszer tiltja a hálózati műveletek futtatását a felhasználói felületért felelős fő szálon (`Main UI Thread`), mert a hálózati késleltetés a kijelző lefagyását idézné elő (`NetworkOnMainThreadException`).

A megoldást a **Kotlin Coroutines** és a **ViewModel** (`MainViewModel.kt`) biztosítja:
- A `viewModelScope.launch` blokk automatikusan a háttérben futtatja a hálózati kéréseket, új lekérdezés indításakor pedig megszakítja a korábbi futó `Job`-ot a versenyhelyzetek elkerülésére.
- Az állapotot a reaktív `StateFlow<UiState>` tárolja, amely három egymást kizáró állapotot vesz fel:
  - `UiState.Loading`: Töltőkarika megjelenítése.
  - `UiState.Success`: A sikeresen beérkezett adatok átadása a felületnek.
  - `UiState.Error`: Hiba esetén felhasználóbarát hibaüzenet és „Újrapróbálkozás” gomb.

### 4.3. Felhasználói felület: Jetpack Compose & Material 3
Az alkalmazás teljes egészében a deklaratív **Jetpack Compose** technológiával készült:
- **`DashboardScreen`**: A fő elrendezést biztosító képernyő, amely a ViewModel állapotát figyeli (`collectAsState()`).
- **`StatCard` és háttértár-kártyák**: Újrafelhasználható kártyakomponensek a CPU, RAM, üzemidő és az aktív storage poolok (`local`, `local-lvm` stb.) kiemelésére.
- **`ServerCard`**: A virtuális gépeket és konténereket megjelenítő kártya, amely zöld ("Online") vagy szürke ("Offline") címkével jelzi a futási státuszt.
- **`SettingsDialog`**: Párbeszédablak, ahol a backend URL és az API-kulcs futásidejűleg módosítható (emulátoros `http://10.0.2.2:8000/` és fizikai telefonos Tailscale HTTPS eléréshez egyaránt).

---

## 5. Tesztelési eredmények és a megvalósított rendszer bemutatása

A rendszert éles környezetben teszteltük: a FastAPI backend egy **Windows-laptopon** futott, amelyhez a Proxmox VE szerver kapcsolódott, az Android alkalmazást pedig Android Studio emulátorban (`http://10.0.2.2:8000/`) és fizikai okostelefonon (**Tailscale-en keresztül, HTTPS-en**) egyaránt ellenőriztük:

1. **Automatizált backend és Android egységtesztek:**
   - 15 db automatizált `pytest` teszt ellenőrzi a backend végpontok működését, a sikeres `DEMO` és `LIVE` válaszokat, a hiányzó és érvénytelen hitelesítést (HTTP 401), az alapértelmezett API-kulcs tiltását éles módban (HTTP 500), valamint az elérhetetlen Proxmox szerver szűrt hibakezelését (HTTP 502).
   - 6 db Android JUnit egységteszt (`ExampleUnitTest.kt`) ellenőrzi a Gson JSON-deszerializációt, az URL-normalizálást, a `MainViewModel` sikeres (`LIVE`) és sikertelen lekéréseit, valamint a hibás kapcsolati beállítások összeomlásmentes kezelését.
2. **Élő rendszereredmények:**
   - **Gazdagép csomópont:** `prox`
   - **CPU:** 12 processzormag (1.4% kihasználtság)
   - **Memória:** 10.8 GB / 15.3 GB RAM (70.3%)
   - **Háttértár:** 15.8 GB / 67.7 GB (23.3%), valamint a részletes storage poolok (`local`, `local-lvm` stb.)
   - **Üzemidő:** 14 nap, 22 óra
   - **Erőforrások:** Mind a 19 virtuális gép és LXC konténer (`haos`, `debian`, `qbittorrent`, `sonarr`, `radarr`, `jellyfin`, `adguard`, `vaultwarden`, `nginx-ui` stb.) sikeresen lekérdezésre és listázásra került.

---

## 6. Összegzés és következtetések

A beadandó készítése során sikerült egy teljes, működőképes és biztonságos mobil infrastruktúra-felügyeleti alkalmazást megvalósítani (`v1.0.0`). A projekt rávilágított a RESTful API-k, az aszinkron szálkezelés (Coroutines) és a típusbiztos JSON-deszerializáció fontosságára a modern Android szoftverfejlesztésben.

A választott architektúra egyszerű, átlátható, mentes a felesleges túlbonyolításoktól, miközben teljes mértékben megfelel a modern iparági és egyetemi elvárásoknak.
