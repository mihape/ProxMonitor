"""Konfigurációs beállítások betöltése környezeti változókból vagy .env fájlból."""

from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(str, Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"


class Settings(BaseSettings):
    # Alkalmazás működési módja: DEMO (mintaadatok) vagy LIVE (valódi Proxmox)
    mode: AppMode = Field(default=AppMode.DEMO, alias="PROXMONITOR_MODE")

    # Mobil kliens hitelesítő API kulcs
    api_key: str = Field(default="titkos-mobil-api-kulcs-valtoztasd-meg", alias="PROXMONITOR_API_KEY")

    # Proxmox VE kapcsolati adatok (LIVE módban kötelezőek)
    proxmox_host: Optional[str] = Field(default=None, alias="PROXMOX_HOST")
    proxmox_node: Optional[str] = Field(default="pve", alias="PROXMOX_NODE")
    proxmox_token_id: Optional[str] = Field(default=None, alias="PROXMOX_TOKEN_ID")
    proxmox_token_secret: Optional[str] = Field(default=None, alias="PROXMOX_TOKEN_SECRET")

    # SSL beállítások
    proxmox_verify_ssl: bool = Field(default=True, alias="PROXMOX_VERIFY_SSL")
    proxmox_ca_cert: Optional[str] = Field(default=None, alias="PROXMOX_CA_CERT")

    # Hálózati kiszolgáló beállítások (0.0.0.0 = elérhető a helyi Wi-Fi hálózatról is, pl. telefonról)
    host: str = Field(default="0.0.0.0", alias="PROXMONITOR_HOST")
    port: int = Field(default=8000, alias="PROXMONITOR_PORT")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def validate_live_config(self) -> None:
        """Ellenőrzi, hogy LIVE módban megvannak-e a szükséges Proxmox beállítások."""
        if self.mode == AppMode.LIVE:
            missing = []
            if not self.proxmox_host:
                missing.append("PROXMOX_HOST")
            if not self.proxmox_token_id:
                missing.append("PROXMOX_TOKEN_ID")
            if not self.proxmox_token_secret:
                missing.append("PROXMOX_TOKEN_SECRET")
            if missing:
                raise ValueError(
                    f"A LIVE üzemmódhoz a következő környezeti változók kötelezőek: {', '.join(missing)}"
                )


# Globális konfiguráció példány
settings = Settings()
