# REST API Specifikáció

Ez a dokumentum a **ProxMonitor** projekt **FastAPI backend** (`v1.0.0`) által biztosított REST API végpontokat és azok tényleges JSON adatformátumait írja le.

---

## 1. Alapbeállítások és protokoll

- **Protokoll és elérési módok:**
  - **Fizikai Android telefonról (tesztelt éles elérés):** **HTTPS** kapcsolaton, **Tailscale** hálózaton keresztül (`https://<laptop-nev>.<tailnet>.ts.net/`), amely a Windows-laptopon futó FastAPI backend (`127.0.0.1:8000`) elé biztosít TLS végpontot.
  - **Helyi fejlesztői környezetben (Android Emulátor):** `http://10.0.2.2:8000/` (`network_security_config.xml` alapján engedélyezett helyi kivétel).
- **Adatformátum:** JSON (`Content-Type: application/json; charset=utf-8`)
- **Hitelesítés:** `X-API-Key: <kulcs>` vagy `Authorization: Bearer <kulcs>` HTTP fejléc (a `/health` végpont kivételével minden végponton kötelező).

---

## 2. Végpontok részletezése

### 2.1. Backend állapotellenőrzés (Health Check)

Nyilvános végpont a backend szolgáltatás elérhetőségének és verziójának ellenőrzésére.

- **Útvonal:** `GET /health`
- **Hitelesítés:** Nem szükséges

#### Sikeres válasz (`HTTP 200 OK`):
```json
{
  "status": "online",
  "application": "ProxMonitor",
  "version": "1.0.0"
}
```

---

### 2.2. Szerver összefoglaló állapot lekérdezése

Visszaadja a gazdagép (Proxmox node) legfontosabb hardveres erőforrás-adatait és az aktív háttértárak (storage poolok) listáját.

- **Útvonal:** `GET /api/v1/status`
- **Hitelesítés:** `X-API-Key: <kulcs>` vagy `Authorization: Bearer <kulcs>`

#### Sikeres válasz (`HTTP 200 OK`):
```json
{
  "mode": "LIVE",
  "node_name": "prox",
  "uptime_seconds": 1284520,
  "uptime_formatted": "14 nap, 20 óra, 48 perc",
  "cpu": {
    "usage_percent": 24.0,
    "cores": 12
  },
  "memory": {
    "used_bytes": 8804682956,
    "total_bytes": 17179869184,
    "formatted": "8.2 GB / 16.0 GB",
    "usage_percent": 51.2
  },
  "storage": {
    "used_bytes": 16941498368,
    "total_bytes": 72722055168,
    "formatted": "15.8 GB / 67.7 GB",
    "usage_percent": 23.3
  },
  "storage_pools": [
    {
      "name": "local",
      "type": "dir",
      "used_bytes": 16941498368,
      "total_bytes": 72722055168,
      "formatted": "15.8 GB / 67.7 GB",
      "usage_percent": 23.3,
      "content": "iso,vztmpl,backup"
    },
    {
      "name": "local-lvm",
      "type": "lvmthin",
      "used_bytes": 158037017257,
      "total_bytes": 168824930304,
      "formatted": "147.2 GB / 157.2 GB",
      "usage_percent": 93.6,
      "content": "images,rootdir"
    }
  ]
}
```

---

### 2.3. Virtuális gépek és konténerek listája

Visszaadja a konfigurált QEMU virtuális gépek (`VM`) és LXC konténerek (`LXC`) állapotát `vmid` szerint rendezve.

- **Útvonal:** `GET /api/v1/resources`
- **Hitelesítés:** `X-API-Key: <kulcs>` vagy `Authorization: Bearer <kulcs>`

#### Sikeres válasz (`HTTP 200 OK`):
```json
{
  "mode": "LIVE",
  "resources": [
    {
      "vmid": 100,
      "name": "Home Assistant",
      "type": "VM",
      "raw_type": "qemu",
      "status": "running",
      "display_status": "Online",
      "cpu_percent": 3.2,
      "memory_used_bytes": 2147483648,
      "memory_formatted": "2.0 GB / 4.0 GB"
    },
    {
      "vmid": 101,
      "name": "Jellyfin",
      "type": "LXC",
      "raw_type": "lxc",
      "status": "running",
      "display_status": "Online",
      "cpu_percent": 12.5,
      "memory_used_bytes": 4294967296,
      "memory_formatted": "4.0 GB / 8.0 GB"
    },
    {
      "vmid": 102,
      "name": "AdGuard Home",
      "type": "LXC",
      "raw_type": "lxc",
      "status": "running",
      "display_status": "Online",
      "cpu_percent": 0.8,
      "memory_used_bytes": 536870912,
      "memory_formatted": "512.0 MB / 1.0 GB"
    }
  ]
}
```

---

## 3. Hibakezelés

Proxmox kapcsolati hiba esetén a backend nem szivárogtat ki belső IP-címeket vagy nyers kivételeket, hanem egységes JSON hibaobjektumot küld vissza:

```json
{
  "error": {
    "type": "PROXMOX_CONNECTION_ERROR",
    "message": "Nem sikerült csatlakozni a Proxmox szerverhez.",
    "status_code": 502
  }
}
```

### Alkalmazott HTTP státuszkódok:
- `200 OK`: Sikeres lekérdezés, adatok mellékelve.
- `401 Unauthorized`: Hiányzó vagy érvénytelen kliens API-kulcs (`detail` mezővel).
- `500 Internal Server Error`: Hiányos vagy érvénytelen szerveroldali `LIVE` konfiguráció (`detail` mezővel).
- `502 Bad Gateway`: A FastAPI backend nem tud csatlakozni a Proxmox VE szerverhez, vagy a Proxmox hibát jelzett.
- `504 Gateway Timeout`: Időtúllépés a Proxmox VE szerver elérésekor.
