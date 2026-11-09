# Változási napló (CHANGELOG)

Minden lényeges módosítás, új funkció és verzió ebben a dokumentumban kerül rögzítésre.

A formátum a [Keep a Changelog](https://keepachangelog.com/hu/1.0.0/) elveit követi, a verziózás pedig a [Szemantikus Verziózást (SemVer)](https://semver.org/lang/hu/) alkalmazza.

---

## [v0.1.0] - 2026-11-01 (Kezdeti állapot)

### Hozzáadva
- **Projektstruktúra inicializálása:**
  - Android Gradle projektstruktúra Kotlin DSL (`.kts`) építőszkriptekkel.
  - Gradle Wrapper v8.13 verzióval.
  - Szigorú, biztonságos `.gitignore` fájl (érzékeny adatok, helyi SDK elérési utak, build fájlok kizárása).
- **Jetpack Compose felhasználói felület (`MainActivity.kt`):**
  - Deklaratív felületkezelés Material 3 komponensekkel.
  - Sötét, modern műszerfal-dizájn (`DashboardScreen`).
  - Újrafelhasználható `StatCard` komponens az erőforrások (CPU, RAM, Tárhely) kijelzésére.
  - Újrafelhasználható `ServerCard` komponens a virtuális gépek és konténerek adatainak megjelenítésére.
  - Statikus mintaadatok (24% CPU, 8.2 GB / 16 GB RAM, 1.8 TB / 4 TB HDD, Home Assistant VM, Jellyfin LXC, AdGuard Home LXC).
- **Dokumentáció:**
  - `README.md`: Átfogó bemutatás, célok és architektúra.
  - `docs/architecture.md`: 3-rétegű architektúra és adatáramlás.
  - `docs/api.md`: Tervezett REST API végpontok specifikációja.
  - `docs/beadando.md`: A tantárgyi követelményeknek megfelelő szakmai leírás.
  - `docs/vedes.md`: Szóbeli védési segédlet, forráskód-magyarázatok és vizsgakérdések.

---

## [v0.3.0] - 2026-11-09

### Hozzáadva
- **Retrofit 2 és Gson REST kliens integráció:**
  - Hálózati engedélyek hozzáadása (`android.permission.INTERNET`, `usesCleartextTraffic`).
  - Típusbiztos Kotlin adatmodellek (`ServerStatusResponse`, `ResourcesResponse`, `ResourceItem`).
  - `ApiService` interfész deklaratív HTTP GET metódusokkal és hitelesítő fejléccel (`X-API-Key`).
  - `RetrofitInstance` singleton objektum a Retrofit kliens konfigurálásához és futásidejű IP-váltáshoz.
- **MVVM architektúra és állapotkezelés:**
  - `MainViewModel`: Coroutine alapú aszinkron hívások (`viewModelScope.launch`) a főszál blokkolása nélkül.
  - `UiState` lezárt interfész (`sealed interface`): `Loading`, `Success`, `Error` állapotok.
- **Dinamikus Jetpack Compose felület:**
  - Valós idejű adatok megjelenítése (CPU terhelés, 12 mag, RAM, tárhely, szerver üzemidő).
  - 19 darab valós virtuális gép és LXC konténer listázása állapotukkal (Online/Offline) és memóriájukkal.
  - "Frissítés" gomb és "Beállítások" párbeszédablak (szerver IP és API kulcs kényelmes módosításához).
  - Hibaállapot kezelése újrapróbálkozás gombbal.
- **Élő emulátoros tesztelés és képernyőkép:**
  - Sikeres élő adatlekérdezés a helyi FastAPI backendről és Proxmox VE szerverről (`screenshots/dashboard_v0.3.0_live.png`).

---

## [v0.2.0] - 2026-11-01

### Hozzáadva
- **FastAPI backend megvalósítása (`backend/`):**
  - Python 3 + FastAPI mikroszolgáltatás aszinkron HTTP támogatással.
  - Pydantic v2 adatmodellek (`ServerStatusResponse`, `ResourcesResponse`, `HealthResponse`).
  - Beépített mintaadat-szolgáltató (`app/demo_provider.py`) a bemutató módhoz.
  - Aszinkron Proxmox VE REST API kliens (`app/proxmox_client.py`) a valós szerverkommunikációhoz (`/api2/json/nodes/{node}/status`, `/api2/json/cluster/resources`).
  - Szigorú üzemmód-elválasztás: DEMO és LIVE mód, hiba esetén a LIVE mód nem esik vissza mintaadatokra.
  - Fejlécalapú hitelesítés: `X-API-Key` és `Authorization: Bearer` támogatása.
  - Swagger UI interaktív dokumentáció a `/docs` végponton.
- **Automatizált tesztek (`backend/tests/test_api.py`):**
  - 9 db automatizált pytest teszt: /health ellenőrzés, hiányzó/hibás auth (401), sikeres DEMO lekérdezések, hibás konfiguráció (500), elérhetetlen Proxmox szerver (502).
- **Konfiguráció és biztonság:**
  - `backend/.env.example` példakonfiguráció.
  - Szigorú SSL ellenőrzés támogatása és localhosthoz kötött indítás (`127.0.0.1:8000`).

---

## [v0.1.0] - 2026-11-01 (Kezdeti állapot)

### [v0.3.0] - Android REST API integráció (Tervezett)
- Retrofit 2 és OkHttp kliens beépítése az Android modulba.
- Adatmodellek (Data Class) létrehozása a JSON válaszok fogadására.
- MVVM (Model-View-ViewModel) architektúra bevezetése: StateFlow alapú reaktív adatfolyam.
- A statikus adatok lecserélése élő backend lekérdezésekre.

### [v0.4.0] - Hibakezelés és felhasználói élmény finomítása (Tervezett)
- Betöltési állapotok (`CircularProgressIndicator`) és hibaüzenetek (Snackbar / hiba kártya).
- Pull-to-refresh (lehúzással frissítés) funkció.
- Offline állapot és időtúllépés (Timeout) intelligens kezelése.

### [v1.0.0] - Végleges egyetemi beadandó (Tervezett)
- Teljes körű tesztelés fizikai eszközön és emulátoron.
- Véglegesített egyetemi dokumentáció és védési prezentáció.
- Release APK készítése és kódvédelem (R8/Proguard).
