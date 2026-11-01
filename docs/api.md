# REST API Specifikáció

Ez a dokumentum a tervezett köztes **FastAPI backend** által biztosított REST API végpontokat és azok JSON adatformátumait írja le.

> [!NOTE]
> A végpontok implementálása a **v0.2.0** mérföldkő során valósul meg. Jelenleg az Android kliens a v0.1.0-ban definiált statikus mintaadatokkal szemlélteti az itt leírt struktúrát.

---

## 1. Alapbeállítások és protokoll

- **Protokoll:** HTTPS (vagy helyi hálózaton HTTP fejlesztési célra)
- **Adatformátum:** JSON (`Content-Type: application/json; charset=utf-8`)
- **Alapértelmezett URI séma:** `https://<backend-host>/api/v1`

---

## 2. Végpontok részletezése

### 2.1. Szerver összefoglaló állapot lekérdezése

Visszaadja a gazdagép (Proxmox node) legfontosabb hardveres erőforrás-adatait.

- **Útvonal:** `GET /api/v1/status`
- **Hitelesítés:** API kulcs / Bearer token a fejlécben (`Authorization: Bearer <token>`)

#### Sikeres válasz (HTTP 200 OK):
```json
{
  "node_name": "pve",
  "uptime_seconds": 1284520,
  "cpu": {
    "usage_percent": 24.0,
    "cores": 8
  },
  "memory": {
    "used_bytes": 8804682956,
    "total_bytes": 17179869184,
    "formatted": "8.2 GB / 16 GB",
    "usage_percent": 51.2
  },
  "storage": {
    "used_bytes": 1979120929996,
    "total_bytes": 4398046511104,
    "formatted": "1.8 TB / 4 TB",
    "usage_percent": 45.0
  }
}
```

---

### 2.2. Virtuális gépek és konténerek listája

Visszaadja a konfigurált virtuális gépek (VM) és konténerek (LXC) állapotát.

- **Útvonal:** `GET /api/v1/resources`
- **Hitelesítés:** Bearer token

#### Sikeres válasz (HTTP 200 OK):
```json
{
  "resources": [
    {
      "vmid": 100,
      "name": "Home Assistant",
      "type": "qemu",
      "display_type": "VM",
      "status": "running",
      "display_status": "Online",
      "cpu_percent": 3.2,
      "memory_used_bytes": 2147483648
    },
    {
      "vmid": 101,
      "name": "Jellyfin",
      "type": "lxc",
      "display_type": "LXC",
      "status": "running",
      "display_status": "Online",
      "cpu_percent": 12.5,
      "memory_used_bytes": 4294967296
    },
    {
      "vmid": 102,
      "name": "AdGuard Home",
      "type": "lxc",
      "display_type": "LXC",
      "status": "running",
      "display_status": "Online",
      "cpu_percent": 0.8,
      "memory_used_bytes": 536870912
    }
  ]
}
```

---

## 3. Hibakezelési szabvány (RFC 7807 alapú)

Hiba esetén az API szabványos JSON formátumú válaszobjektumot küld vissza megfelelő HTTP státuszkóddal:

```json
{
  "error": {
    "code": "PROXMOX_UNREACHABLE",
    "message": "A Proxmox VE szerver nem érhető el vagy időtúllépés történt.",
    "status_code": 503
  }
}
```

### Tipikus státuszkódok:
- `200 OK`: A kérés sikeres, adatok mellékelve.
- `401 Unauthorized`: Hiányzó vagy érvénytelen kliens token.
- `502 Bad Gateway`: A FastAPI nem tud csatlakozni a Proxmox szerverhez.
- `503 Service Unavailable`: A Proxmox szerver karbantartás alatt van vagy offline.
