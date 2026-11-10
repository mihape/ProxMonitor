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
                            │ HTTPS / REST (JSON)
                            │ Bearer Token / API kulcs
                            ▼
┌────────────────────────────────────────────────────────┐
│               KÖZTES BACKEND (FastAPI / Python)        │
│  - REST API végpontok kiszolgálása                     │
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
│  - Debian Linux alapú fürt / önálló node               │
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
   Ha a mobilalkalmazás közvetlenül hívná a Proxmoxot, a kliensen kellene tárolni a Proxmox API tokent vagy jelszót. Egy Android APK könnyen visszafejthető (dekompilálható pl. jadx segítségével), így a szerver teljes körű hozzáférése kompromittálódna. A köztes szerver használatával a Proxmox token kizárólag a szerveroldali biztonságos környezetben (környezeti változókban) marad.

2. **Hálózati terhelés és adatminimalizálás (Payload Optimization):**  
   A Proxmox natív API-ja rendkívül részletes, mélyen beágyazott és terjedelmes JSON-t ad vissza (több száz felesleges mezővel). A lassabb mobilhálózaton a felesleges adatforgalom akkumulátor- és sávszélesség-pazarló. A FastAPI backend csak azt a 4-5 lényeges adatmezőt továbbítja, amire a mobil UI-nak ténylegesen szüksége van.

3. **Hálózati réteg és végpontvédelem:**  
   A Proxmox adminisztrációs felületét (8006-os port) nem ajánlott közvetlenül az internetre kiengedni. A köztes backend egy védett, szigorúan korlátozott és dedikált felületet nyújt a külvilág felé.

---

## 3. Adatáramlás és életciklus

1. **Felhasználói interakció / Képernyő megnyitása:**
   - A `MainActivity` indításakor a `DashboardScreen` feliratkozik a ViewModel állapotára.
2. **Kérés indítása (Aszinkron):**
   - A mobilalkalmazás Coroutine háttérszálon (IO dispatcher) keresztül HTTP GET kérést küld a backend `/api/v1/status` és `/api/v1/resources` végpontjaira a Retrofit segítségével.
3. **Backend feldolgozás:**
   - A FastAPI fogadja a kérést, ellenőrzi a kliens hitelesítését, majd meghívja a Proxmox `/api2/json/nodes/{node}/status` API-ját.
   - A Proxmox válaszából kinyeri a releváns mutatókat: `cpu` százalék, használt és maximális `memory`, használt és maximális `disk`.
4. **JSON válasz visszaküldése:**
   - A backend egy egyszerűsített, tiszta JSON objektumot ad vissza HTTP 200 OK kíséretében.
5. **Kliensoldali deszerializáció és UI frissítés:**
   - A Retrofit a JSON választ Kotlin típusbiztos adatmodellé alakítja (`ServerStatusResponse`).
   - A ViewModel frissíti a belső `StateFlow` állapotot.
   - A Jetpack Compose automatikusan újrarajzolja (Recomposition) az érintett `StatCard` és `ServerCard` komponenseket a friss adatokkal.
