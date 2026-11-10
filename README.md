# ProxMonitor

> **Miskolci Egyetem – Mobilprogramozás tantárgyi beadandó (FOSZ)**  
> **Témakör:** REST API és JSON-feldolgozás Android-alkalmazásokban  
> **Szerző:** Mihalek Péter  
> **Aktuális verzió:** v1.0.0 (Végleges beadási kiadás – Android kliens + FastAPI backend élő Proxmox kapcsolatban)

---

## 1. A projekt célja

A **ProxMonitor** egy modern, natív Android-alkalmazás, amely egy otthoni vagy intézményi **Proxmox Virtual Environment (PVE)** hipervizor állapotának valós idejű megfigyelését teszi lehetővé mobil eszközről.

A rendszer célja, hogy a szerverüzemeltető közvetlen webes felületre lépés nélkül, egy kézre álló mobilalkalmazásban ellenőrizhesse:
- A fizikai csomópont (node) hardveres kihasználtságát (12 CPU mag terhelése, memória- és háttértár-foglaltság, részletes storage poolok, szerver üzemidő).
- A futó virtuális gépek (QEMU VM) és konténerek (LXC) állapotát (Online/Offline) és azok memóriafogyasztását.

A projekt a **Mobilprogramozás** tantárgy követelményeinek megfelelően a **RESTful hálózati kommunikáció**, az aszinkron **JSON-deszerializáció**, valamint a modern deklaratív **Jetpack Compose** felületépítés és egyszerű **MVVM** architektúra gyakorlati megvalósítását mutatja be.

---

## 2. Rendszerarchitektúra és technológiák

A rendszer három fő komponensből áll. A tesztelt elrendezésben a köztes FastAPI backend egy **Windows-laptopon** fut (`127.0.0.1:8000`), amelyet a fizikai Android telefon **Tailscale-en keresztül HTTPS-en** (emulátor esetén pedig a `http://10.0.2.2:8000/` helyi címen) ér el:

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
│  - Biztonságos tokenkezelés     │
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

### Felhasznált technológiák:

- **Mobil kliens (Android):**
  - **Nyelv:** Kotlin (100%-ban típusbiztos, null-safe)
  - **UI keretrendszer:** Jetpack Compose & Material 3 (deklaratív felület)
  - **Architektúra:** Egyszerű MVVM (Model-View-ViewModel) `StateFlow` állapotkezeléssel
  - **Hálózatkezelés:** Retrofit 2, OkHttp 3 és Gson Converter (JSON-feldolgozás)
  - **Aszinkronitás:** Kotlin Coroutines (`viewModelScope.launch`, `suspend fun`)
  - **Build rendszer:** Gradle Kotlin DSL (`.kts`)

- **Köztes Backend (Python / FastAPI – Windows-laptop):**
  - **Keretrendszer:** FastAPI & Uvicorn aszinkron ASGI szerver
  - **Adatvalidáció:** Pydantic v2 modellek
  - **Proxmox kommunikáció:** `httpx` aszinkron HTTP kliens
  - **Hitelesítés:** `X-API-Key` vagy `Authorization: Bearer`
  - **Biztonság:** A Proxmox API token kizárólag a szerver `.env` fájljában található, az Android APK nem tartalmaz beégetett szervertitkokat.

---

## 3. Funkciók és megvalósítási állapot

| Funkció | Leírás | Állapot |
| :--- | :--- | :--- |
| **Összesítő műszerfal** | Főképernyő a szerver állapotának áttekintésére | **Kész (v1.0.0)** |
| **CPU terhelés kártya** | Processzorterheltség és magok száma (12 mag) | **Kész (Élő adatokkal - v1.0.0)** |
| **Memória kártya** | RAM használat és százalék (10.8 GB / 15.3 GB) | **Kész (Élő adatokkal - v1.0.0)** |
| **Háttértárak és lemezek** | Részletes storage pool kártyák (`local`, `local-lvm` stb.) | **Kész (Élő adatokkal - v1.0.0)** |
| **Szerver üzemidő** | Emberi formátumban kijelzett üzemidő (14 nap...) | **Kész (Élő adatokkal - v1.0.0)** |
| **VM / LXC lista kártyák** | 19 db valós entitás (`haos`, `debian`, `jellyfin` stb.) | **Kész (Élő adatokkal - v1.0.0)** |
| **FastAPI köztes réteg** | Python mikroszolgáltatás a PVE API lekérdezésére | **Kész (v1.0.0)** |
| **Dinamikus REST API hívás**| Valós idejű adatok lekérése a telefonról (Retrofit) | **Kész (v1.0.0)** |
| **Hiba- és állapotkezelés** | Töltésjelző, hálózati hiba, Újrapróbálkozás gomb | **Kész (v1.0.0)** |
| **Kapcsolati beállítások** | Szerver URL és kulcs futásidejű módosítása (⚙ gomb) | **Kész (v1.0.0)** |
| **Tailscale HTTPS elérés** | Fizikai telefonos kapcsolat HTTPS-en a laptop backendhez | **Kész (v1.0.0)** |

---

## 4. Képernyőképek

### Élő működés a valódi Proxmox szerver adataival:
![ProxMonitor Élő Dashboard](screenshots/dashboard_v0.3.0_live.png)

---

## 5. Telepítés és indítás (klónozás után)

### 5.1. A Python backend telepítése és indítása (Windows-laptop)

1. Klónozás után lépj be a `backend` könyvtárba, hozd létre a virtuális környezetet és telepítsd a függőségeket:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```
2. Másold le a példakonfigurációt `.env` néven:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Szerkeszd a `.env` fájlt:
   - **Gyors kipróbáláshoz (`DEMO` mód):** Az alapértelmezett `PROXMONITOR_MODE=DEMO` beállítással a backend Proxmox szerver nélkül is azonnal indítható.
   - **Éles Proxmox kapcsolathoz (`LIVE` mód):** Állítsd be a `PROXMONITOR_MODE=LIVE` értéket, adj meg egy egyedi, erős `PROXMONITOR_API_KEY` kulcsot (az alapértelmezett példakulccsal a `LIVE` mód biztonsági okból nem indul el), valamint töltsd ki a `PROXMOX_HOST`, `PROXMOX_NODE`, `PROXMOX_TOKEN_ID` és `PROXMOX_TOKEN_SECRET` változókat.
4. Indítsd el a backend szervert:
   ```powershell
   .\.venv\Scripts\python run.py
   ```
5. A szerver alapértelmezetten a biztonságos `http://127.0.0.1:8000` címen fut. A Swagger UI felület elérhető a böngészőben: `http://127.0.0.1:8000/docs`.

### 5.2. Az Android alkalmazás fordítása és csatlakoztatása

1. Nyisd meg a projekt gyökerét Android Studio-ban, vagy fordítsd le parancssorból a projekt gyökérkönyvtárában:
   ```powershell
   .\gradlew.bat assembleDebug
   ```
2. Indítsd el az alkalmazást, majd a jobb felső sarokban található **⚙ Beállítások** gombbal add meg a backend URL-t és a `.env` fájlban beállított `PROXMONITOR_API_KEY` kulcsot:
   - **Android Emulátorban:** Alapértelmezetten a `http://10.0.2.2:8000/` címet használja, amely közvetlenül eléri a Windows-laptopon futó backend `127.0.0.1:8000` portját (`network_security_config.xml` helyi fejlesztői kivételével).
   - **Fizikai Android telefonon (Tailscale HTTPS):** A Windows-laptopon futó FastAPI backendet Tailscale HTTPS végpontként (`tailscale serve --bg 8000`) publikálva a telefon a `https://<laptop-nev>.<tailnet>.ts.net/` címen keresztül, titkosított HTTPS kapcsolaton éri el a szervert. (Séma nélkül megadott távoli címekhez az alkalmazás automatikusan `https://` előtagot állít be.)

### 5.3. Automatizált tesztek futtatása

- **Android egységtesztek (6 db JUnit teszt):**
  ```powershell
  .\gradlew.bat testDebugUnitTest
  ```
- **Python backend tesztek (15 db `pytest` teszt):**
  ```powershell
  .\backend\.venv\Scripts\python -m pytest backend/tests/test_api.py -v
  ```

---

## 6. Szakmai dokumentáció

A tantárgyhoz kapcsolódó részletes szakmai dokumentumok a [`docs/`](docs/) mappában találhatók:
- [Rendszerarchitektúra és adatáramlás](docs/architecture.md)
- [REST API specifikáció és JSON szerkezetek](docs/api.md)
- [Tantárgyi szakmai beadandó dolgozat](docs/beadando.md)
