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

## Tervezett mérföldkövek:

### [v0.2.0] - FastAPI backend megvalósítása (Tervezett)
- Python 3 + FastAPI mikroszolgáltatás létrehozása a `backend/` könyvtárban.
- Proxmox VE REST API integráció (`pve-api-token` alapú biztonságos autentikáció).
- Egyszerűsített, mobilra optimalizált REST végpontok kialakítása (`/api/status`, `/api/nodes`, `/api/resources`).

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
