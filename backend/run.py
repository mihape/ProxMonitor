"""Kényelmi indítószkript a FastAPI fejlesztői szerverhez."""

import sys
from pathlib import Path
import uvicorn

# Biztosítjuk, hogy a 'backend' mappa benne legyen a Python keresési útvonalában
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import settings

if __name__ == "__main__":
    print(f"============================================================")
    print(f"  ProxMonitor Backend Szerver Indítása")
    print(f"  Üzemmód:      {settings.mode.value}")
    print(f"  Kiszolgáló:   {settings.host}:{settings.port}")
    print(f"  Dokumentáció: http://127.0.0.1:{settings.port}/docs")
    print(f"============================================================")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
