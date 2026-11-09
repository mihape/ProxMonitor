# Szakmai Beadandó Dolgozat

> **Intézmény:** Miskolci Egyetem – Gépészmérnöki és Informatikai Kar  
> **Képzés:** Felsőoktatási szakképzés (FOSZ)  
> **Tantárgy:** Mobilprogramozás  
> **Témakör:** REST API és JSON-feldolgozás Android-alkalmazásokban  
> **Projekt címe:** ProxMonitor – Proxmox VE infrastruktúra-felügyelet natív Android környezetben  
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
- másodpercek alatt ellenőrizhesse a szerver pillanatnyi processzor-, memória- és háttértár-terhelését,
- nyomon kövesse a virtuális gépek (QEMU VM) és konténerek (LXC) futási állapotát,
- biztonságos csatornán keresztül, a legkisebb jogosultság elve mellett férjen hozzá a statisztikákhoz.

---

## 3. Rendszerarchitektúra és komponensek kapcsolata

A rendszer háromrétegű kliens-szerver architektúrára épül:

```text
┌─────────────────────────────────┐
│       ANDROID MOBIL KLIENS      │
│  - Jetpack Compose & Material 3 │
│  - MainViewModel & UiState      │
│  - Retrofit 2 & Gson konverter  │
└────────────────┬────────────────┘
                 │ HTTP / REST (JSON)
                 │ Fejléc: X-API-Key: <kulcs>
                 ▼
┌─────────────────────────────────┐
│       KÖZTES BACKEND API        │
│  - Python 3 + FastAPI           │
│  - Pydantic v2 adatmodellek     │
│  - Proxmox API Token védelem    │
└────────────────┬────────────────┘
                 │ HTTPS / REST (PVE API)
                 │ Fejléc: PVEAPIToken=root@pam!mobile=UUID
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
   A Proxmox API token korlátlan hozzáférést biztosíthat a teljes virtualizációs környezethez. Egy Android APK fájl könnyen visszafejthető (dekompilálható), így az alkalmazáskódban tilos érzékeny API-kulcsokat vagy jelszavakat tárolni. A köztes Python backend elrejti a Proxmox hitelesítést, és a telefon felé egy szigorúan korlátozott, dedikált API-kulcsot (`X-API-Key`) kér.
2. **Hálózati terhelés és adatminimalizálás:**  
   A Proxmox natív API válaszai több száz technikai paramétert tartalmaznak. A mobilhálózat sávszélességének és akkumulátorának kímélése érdekében a FastAPI backend előfeldolgozza az adatokat, és kizárólag a telefonos felülethez szükséges 4-5 lényeges mezőt továbbítja tiszta JSON formátumban.

---

## 4. Az Android kliens megvalósítása

### 4.1. Hálózati réteg: Retrofit 2 és Gson
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

A válaszok deszerializációját a **Gson Converter** végzi. A beérkező szöveges JSON adatokat típusbiztos Kotlin adatosztályokká (`data class`) konvertálja:
```kotlin
data class ServerStatusResponse(
    val mode: String,
    val node_name: String,
    val uptime_formatted: String,
    val cpu: CpuInfo,
    val memory: MemoryInfo,
    val storage: StorageInfo
)
```

### 4.2. Aszinkron működés és MVVM architektúra
Az Android rendszer tiltja a hálózati műveletek futtatását a felhasználói felületért felelős fő szálon (`Main UI Thread`), mert a hálózati késleltetés a kijelző lefagyását idézné elő (`NetworkOnMainThreadException`).

A megoldást a **Kotlin Coroutines** és a **ViewModel** (`MainViewModel.kt`) biztosítja:
- A `viewModelScope.launch` blokk automatikusan a háttérben futtatja a hálózati kéréseket.
- Az állapotot a reaktív `StateFlow<UiState>` tárolja, amely három egymást kizáró állapotot vesz fel:
  - `UiState.Loading`: Töltőkarika megjelenítése.
  - `UiState.Success`: A sikeresen beérkezett adatok átadása a felületnek.
  - `UiState.Error`: Hiba esetén felhasználóbarát hibaüzenet és „Újrapróbálkozás” gomb.

### 4.3. Felhasználói felület: Jetpack Compose & Material 3
Az alkalmazás teljes egészében a legújabb deklaratív **Jetpack Compose** technológiával készült, elhagyva az elavult XML alapú nézeteket:
- **`DashboardScreen`**: A fő elrendezést biztosító képernyő, amely a ViewModel állapotát figyeli (`collectAsState()`).
- **`StatCard`**: Újrafelhasználható kártyakomponens a CPU, RAM, tárhely és üzemidő kiemelésére egyedi színekkel és lekerekített sarkokkal.
- **`ServerCard`**: A virtuális gépeket és konténereket megjelenítő kártya, amely zöld ("Online") vagy szürke ("Offline") címkével jelzi a futási státuszt.
- **`SettingsDialog`**: Párbeszédablak, ahol a szerver IP-címe és az API kulcs futásidejűleg módosítható (így emulátoron és fizikai eszközön is könnyen használható).

---

## 5. Tesztelési eredmények és a megvalósított rendszer bemutatása

A rendszert éles környezetben, valós Proxmox VE szerverrel és Android Studio emulátorral teszteltük:

1. **Automatizált backend tesztek:**
   - 9 db automatizált `pytest` teszt ellenőrzi a végpontok működését, a sikeres válaszokat, a hiányzó és érvénytelen hitelesítést (HTTP 401), valamint az elérhetetlen Proxmox szerver hibakezelését (HTTP 502).
2. **Élő rendszereredmények:**
   - **Gazdagép csomópont:** `prox`
   - **CPU:** 12 processzormag (1.4% kihasználtság)
   - **Memória:** 10.8 GB / 15.3 GB RAM (70.3%)
   - **Háttértár:** 15.8 GB / 67.7 GB (23.3%)
   - **Üzemidő:** 14 nap, 22 óra
   - **Erőforrások:** Mind a 19 virtuális gép és LXC konténer (`haos`, `debian`, `qbittorrent`, `sonarr`, `radarr`, `jellyfin`, `adguard`, `vaultwarden`, `nginx-ui` stb.) sikeresen lekérdezésre és listázásra került.

---

## 6. Összegzés és következtetések

A beadandó készítése során sikerült egy teljes, működőképes és biztonságos mobil infrastruktúra-felügyeleti alkalmazást megvalósítani. A projekt rávilágított a RESTful API-k, az aszinkron szálkezelés (Coroutines) és a típusbiztos JSON-deszerializáció fontosságára a modern Android szoftverfejlesztésben.

A választott architektúra egyszerű, átlátható, mentes a felesleges túlbonyolításoktól, miközben teljes mértékben megfelel a modern iparági és egyetemi elvárásoknak.
