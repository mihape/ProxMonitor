# Változási napló (CHANGELOG)

Minden lényeges módosítás, új funkció és verzió ebben a dokumentumban kerül rögzítésre.

A formátum a [Keep a Changelog](https://keepachangelog.com/hu/1.0.0/) elveit követi, a verziózás pedig a [Szemantikus Verziózást (SemVer)](https://semver.org/lang/hu/) alkalmazza.

---

## [v0.3.0] - 2026-11-09

### Hozzáadva
- **Retrofit 2 és Gson REST kliens integráció:**
  - Hálózati engedély (`android.permission.INTERNET`) és szigorított hálózati biztonsági konfiguráció (`res/xml/network_security_config.xml`: külső kapcsolatokon kötelező HTTPS, helyi fejlesztői `10.0.2.2` / `127.0.0.1` / `localhost` címeken engedélyezett HTTP).
  - Típusbiztos Kotlin adatmodellek (`ServerStatusResponse`, `StoragePoolItem`, `ResourcesResponse`, `ResourceItem`).
  - `ApiService` interfész deklaratív HTTP GET metódusokkal és hitelesítő fejléccel (`X-API-Key`).
  - `RetrofitInstance` singleton objektum URL-normalizálással, validációval és futásidejű szervercím-váltással.
- **MVVM architektúra és állapotkezelés:**
  - `MainViewModel`: Coroutine alapú aszinkron hívások (`viewModelScope.launch`) a főszál blokkolása nélkül, a korábbi hálózati `Job` megszakításával a versenyhelyzetek elkerülésére.
  - `UiState` lezárt interfész (`sealed interface`): `Loading`, `Success`, `Error` állapotok.
- **Dinamikus Jetpack Compose felület:**
  - Valós idejű adatok megjelenítése (CPU terhelés, 12 mag, RAM, részletes háttértárak/storage poolok, szerver üzemidő).
  - 19 darab valós virtuális gép és LXC konténer listázása állapotukkal (Online/Offline) és memóriájukkal.
  - "Frissítés" gomb és "Beállítások" párbeszédablak maszkolt API-kulcs beviteli mezővel.
  - Hibaállapot kezelése újrapróbálkozás gombbal.
- **Tesztelés és biztonsági megerősítések:**
  - Android JUnit egységtesztek (`ExampleUnitTest.kt`) a JSON-deszerializáció, URL-validáció és ViewModel állapotkezelés ellenőrzésére.
  - Bővített backend `pytest` tesztkészlet (`backend/tests/test_api.py`): DEMO és LIVE mód, alapértelmezett API-kulcs tiltása LIVE módban, valamint a Proxmox hibaüzenetek szűrése.
  - Sikeres élő adatlekérdezés a helyi FastAPI backendről és Proxmox VE szerverről (`screenshots/dashboard_v0.3.0_live.png`).

---

## [v0.2.0] - 2026-11-01

### Hozzáadva
- **FastAPI backend megvalósítása (`backend/`):**
  - Python 3 + FastAPI mikroszolgáltatás aszinkron HTTP támogatással.
  - Pydantic v2 adatmodellek (`ServerStatusResponse`, `ResourcesResponse`, `HealthResponse`).
  - Beépített mintaadat-szolgáltató (`app/demo_provider.py`) a bemutató módhoz.
  - Aszinkron Proxmox VE REST API kliens (`app/proxmox_client.py`) a valós szerverkommunikációhoz (`/api2/json/nodes/{node}/status`, `/api2/json/nodes/{node}/storage`, `/api2/json/cluster/resources`).
  - Szigorú üzemmód-elválasztás: DEMO és LIVE mód, hiba esetén a LIVE mód nem esik vissza mintaadatokra.
  - Fejlécalapú hitelesítés: `X-API-Key` és `Authorization: Bearer` támogatása.
  - Swagger UI interaktív dokumentáció a `/docs` végponton.
- **Konfiguráció és biztonság:**
  - `backend/.env.example` példakonfiguráció.
  - Szigorú SSL ellenőrzés támogatása és alapértelmezett localhosthoz kötött indítás (`127.0.0.1:8000`).

---

## [v0.1.0] - 2026-11-01 (Kezdeti állapot)

### Hozzáadva
- **Projektstruktúra inicializálása:**
  - Android Gradle projektstruktúra Kotlin DSL (`.kts`) építőszkriptekkel.
  - Szigorú, biztonságos `.gitignore` fájl (érzékeny adatok, helyi SDK elérési utak, build fájlok kizárása).
- **Jetpack Compose felhasználói felület (`MainActivity.kt`):**
  - Deklaratív felületkezelés Material 3 komponensekkel.
  - Sötét, modern műszerfal-dizájn (`DashboardScreen`).
  - Újrafelhasználható `StatCard` komponens az erőforrások (CPU, RAM, Tárhely) kijelzésére.
  - Újrafelhasználható `ServerCard` komponens a virtuális gépek és konténerek adatainak megjelenítésére.
  - Statikus mintaadatok a kezdeti elrendezés bemutatásához.
- **Dokumentáció:**
  - `README.md`: Átfogó bemutatás, célok és architektúra.
  - `docs/architecture.md`: 3-rétegű architektúra és adatáramlás.
  - `docs/api.md`: REST API végpontok specifikációja.
  - `docs/beadando.md`: A tantárgyi követelményeknek megfelelő szakmai leírás.
