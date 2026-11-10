# Rendszerarchitektúra és adatáramlás

A **ProxMonitor** projekt egy modern, háromrétegű elosztott architektúrára épül, amely garantálja a hálózati biztonságot, az erőforrások optimális kihasználását és a tiszta felelősségmegosztást (Separation of Concerns).

---

## 1. Architekturális áttekintés

```text
┌────────────────────────────────────────────────────────┐
│                   ANDROID MOBIL KLIENS                 │
│  - Jetpack Compose UI (Material 3)                     │
│  - ViewModel (UI állapotkezelés: StateFlow)            │
│  - Retrofit / OkHttp (REST API kommunikáció)           │
│  - JSON Deszerializáció (Kotlin Data Classes)          │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ HTTPS (Tailscale) / HTTP (Emulátor: 10.0.2.2)
                            │ X-API-Key / Bearer Token
                            ▼
┌────────────────────────────────────────────────────────┐
│      KÖZTES BACKEND (FastAPI / Python – Windows-laptop)│
│  - REST API végpontok kiszolgálása (127.0.0.1:8000)    │
│  - Proxmox API Token biztonságos tárolása (.env)       │
│  - Adattranszformáció és hibaszűrés                    │
│  - Mobilra optimalizált, szűrt JSON válaszok           │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ HTTPS / REST (JSON)
                            │ PVEAPIToken=USER@REALM!TOKENID=UUID
                            ▼
┌────────────────────────────────────────────────────────┐
│                 PROXMOX VE HYPERVISOR                  │
│  - Debian Linux alapú fürt / önálló node ('prox')      │
│  - PVE REST API (/api2/json/...)                       │
│  - QEMU virtuális gépek és LXC konténerek kezelése     │
│  - Hardver statisztikák (rrdcached, pvestatd)          │
└────────────────────────────────────────────────────────┘
```

---

## 2. A rétegek felelőssége és indoklása

### 2.1. Miért nem csatlakozik a telefon közvetlenül a Proxmoxhoz?
Egy egyetemi védésen gyakori kérdés: *„Miért van szükség egy köztes Python backendre, ha a Proxmoxnak már van saját REST API-ja?”*

A közvetlen kapcsolat elkerülésének három alapvető biztonsági és szoftvertervezési oka van:

1. **Titkok védelme (Credential Security):**  
   Ha a mobilalkalmazás közvetlenül hívná a Proxmoxot, a kliensen kellene tárolni a Proxmox API tokent vagy jelszót. Egy Android APK könnyen visszafejthető (dekompilálható pl. jadx segítségével), így a szerver teljes körű hozzáférése kompromittálódna. A köztes szerver használatával a Proxmox token kizárólag a szerveroldali biztonságos környezetben (a Windows-laptopon futó backend `.env` fájljában) marad.

2. **Hálózati terhelés és adatminimalizálás (Payload Optimization):**  
   A Proxmox natív API-ja rendkívül részletes, mélyen beágyazott és terjedelmes JSON-t ad vissza (több száz felesleges mezővel). A lassabb mobilhálózaton a felesleges adatforgalom akkumulátor- és sávszélesség-pazarló. A FastAPI backend csak a lényeges, előformázott adatmezőket továbbítja, amire a mobil UI-nak ténylegesen szüksége van.

3. **Hálózati réteg, Tailscale HTTPS és végpontvédelem:**  
   A Proxmox adminisztrációs felületét (8006-os port) nem ajánlott közvetlenül kitenni. A tesztelt rendszerben a FastAPI backend egy Windows-laptopon fut helyi `127.0.0.1:8000` kötéssel, amelyet a fizikai Android telefon **Tailscale-en keresztül, HTTPS-en** ér el, míg az Android Studio emulátor a helyi `http://10.0.2.2:8000/` csatornát használja.

---

## 3. Adatáramlás és életciklus

1. **Felhasználói interakció / Képernyő megnyitása:**
   - A `MainActivity` indításakor a `DashboardScreen` feliratkozik a `MainViewModel` állapotára (`StateFlow<UiState>`).
2. **Kérés indítása (Aszinkron):**
   - A mobilalkalmazás Coroutine háttérszálon (`viewModelScope.launch`) keresztül HTTP GET kérést küld a backend `/api/v1/status` és `/api/v1/resources` végpontjaira a Retrofit segítségével, a korábbi esetleg még futó lekérdezés (`Job`) megszakításával.
3. **Backend feldolgozás:**
   - A FastAPI fogadja a kérést, ellenőrzi a kliens API-kulcsát (`verify_api_key`) és a `LIVE` konfiguráció érvényességét (`validate_live_config`), majd meghívja a Proxmox `/api2/json/nodes/{node}/status`, `/api2/json/nodes/{node}/storage` és `/api2/json/cluster/resources?type=vm` végpontjait.
   - A Proxmox válaszaiból kinyeri és formázza a releváns mutatókat: `cpu`, `memory`, `storage`, az aktív `storage_pools` listát, valamint a virtuális gépek és LXC konténerek adatait.
4. **JSON válasz visszaküldése:**
   - A backend egy egyszerűsített, Pydantic modellekkel validált JSON objektumot ad vissza `HTTP 200 OK` kíséretében.
5. **Kliensoldali deszerializáció és UI frissítés:**
   - A Retrofit Gson konvertere a JSON választ Kotlin típusbiztos adatmodellekké alakítja (`ServerStatusResponse`, `ResourcesResponse`).
   - A ViewModel frissíti a belső `StateFlow` állapotot (`UiState.Success`).
   - A Jetpack Compose automatikusan újrarajzolja (Recomposition) az érintett `StatCard`, háttértár és `ServerCard` komponenseket a friss adatokkal.
