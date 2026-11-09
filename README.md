# ProxMonitor

> **Miskolci Egyetem – Mobilprogramozás tantárgyi beadandó**  
> **Témakör:** REST API és JSON-feldolgozás Android-alkalmazásokban  
> **Szerző:** Mihalek Péter  
> **Aktuális verzió:** v0.3.0 (Android REST API és JSON-feldolgozás élő adatokkal)

---

## 1. A projekt célja

A **ProxMonitor** egy modern, natív Android-alkalmazás, amely egy otthoni vagy intézményi **Proxmox Virtual Environment (PVE)** szerver állapotának valós idejű megfigyelését teszi lehetővé mobil eszközről.

A rendszer célja, hogy a szerverüzemeltető vagy rendszergazda közvetlen webes felületre lépés nélkül, egy kézre álló mobilalkalmazásban ellenőrizhesse:
- A fizikai csomópont (node) hardveres kihasználtságát (CPU, memória, háttértár).
- A futó virtuális gépek (QEMU/KVM VM) és konténerek (LXC) állapotát és erőforrás-fogyasztását.

A projekt kiemelt oktatási célja a **kliens-szerver architektúra**, a **RESTful hálózati kommunikáció**, az aszinkron **JSON-deszerializáció**, valamint a modern deklaratív **Jetpack Compose** felhasználói felület gyakorlati bemutatása.

---

## 2. Rendszerarchitektúra és technológiák

A rendszer három fő komponensből áll:

```text
┌─────────────────────────┐
│   Android Kliens        │ (Kotlin + Jetpack Compose + Retrofit)
└────────────┬────────────┘
             │ HTTPS / REST (JSON)
             ▼
┌─────────────────────────┐
│   Köztes Backend API    │ (Python + FastAPI) [Tervezett – 2. fázis]
└────────────┬────────────┘
             │ Proxmox REST API (API Token Auth)
             ▼
┌─────────────────────────┐
│   Proxmox VE Szerver    │ (PVE Node + QEMU VM + LXC)
└─────────────────────────┘
```

### Felhasznált technológiák:

- **Mobil kliens (Android):**
  - **Nyelv:** Kotlin (100%-ban típusbiztos, null-safe)
  - **UI keretrendszer:** Jetpack Compose & Material 3 (deklaratív felületépítés)
  - **Architektúra:** MVVM (Model-View-ViewModel) állapotkezelés [Tervezett integráció: v0.3.0]
  - **Hálózatkezelés:** Retrofit 2 & OkHttp 3, Kotlinx Serialization / Gson [Tervezett integráció: v0.3.0]
  - **Build rendszer:** Gradle (Kotlin DSL - `.kts`)

- **Köztes Backend (Tervezett – v0.2.0):**
  - **Nyelv & Keretrendszer:** Python 3 + FastAPI
  - **Hitelesítés:** Proxmox API Token (PVEAPIToken) biztonságos, szerveroldali tárolása
  - **Szerepe:** Védi a Proxmox API hitelesítő adatait; egyszerűsített, kifejezetten a mobilra optimalizált JSON válaszokat ad.

---

## 3. Funkciók és megvalósítási állapot

| Funkció | Leírás | Állapot |
| :--- | :--- | :--- |
| **Összesítő műszerfal** | Főképernyő a szerver állapotának áttekintésére | **Kész (v0.1.0)** |
| **CPU terhelés kártya** | Pillanatnyi processzorkihasználtság és magok száma | **Kész (Élő adatokkal - v0.3.0)** |
| **Memória kártya** | Felhasznált / összes RAM és százalékos arány | **Kész (Élő adatokkal - v0.3.0)** |
| **Tárhely kártya** | Merevlemez/tárterület foglaltság és százalék | **Kész (Élő adatokkal - v0.3.0)** |
| **VM / LXC lista kártyák** | Név, VMID, típus (VM/LXC), memória és státusz | **Kész (19 élő entitás - v0.3.0)** |
| **FastAPI köztes réteg** | Python mikroszolgáltatás a PVE API lekérdezésére | **Kész (v0.2.0)** |
| **Dinamikus REST API hívás**| Valós idejű adatok lekérése a telefonról (Retrofit) | **Kész (v0.3.0)** |
| **Hiba- és állapotkezelés** | Betöltésjelző, hálózati hibák, újrapróbálkozás | **Kész (v0.3.0)** |

---

## 4. Képernyőképek

Az alkalmazás az élő Proxmox VE adatokkal futva az Android emulátoron (v0.3.0):

![ProxMonitor Élő Dashboard](screenshots/dashboard_v0.3.0_live.png)

---

## 5. Telepítés és futtatás

### Követelmények:
- Android Studio Ladybug / Meerkat vagy újabb
- Android SDK (minSdk: 26 - Android 8.0 Oreo, targetSdk: 36)
- Java 11 / JDK 17+ (a Gradle futtatásához)

### Fordítás parancssorból (Windows PowerShell):
```powershell
# Debug APK fordítása
.\gradlew.bat assembleDebug

# Tesztek futtatása
.\gradlew.bat test
```

A lefordított APK fájl helye:
`app/build/outputs/apk/debug/app-debug.apk`

---

## 6. Dokumentáció

A részletes egyetemi és szakmai dokumentáció a [`docs/`](docs/) mappában található:
- [Rendszerarchitektúra és adatáramlás](docs/architecture.md)
- [REST API specifikáció](docs/api.md)
- [Tantárgyi beadandó dolgozat](docs/beadando.md)
- [Szóbeli védési segédlet és vizsgakérdések](docs/vedes.md)
