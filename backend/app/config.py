from enum import Enum
import hashlib
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(str, Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"


# Ismert alapértelmezett API-kulcsok, amelyekkel a LIVE üzemmód biztonsági okból nem indulhat el
INSECURE_DEFAULT_API_KEYS = {
    "",
    "titkos-mobil-api-kulcs-valtoztasd-meg",
    "changeme",
}

# Korábban visszavont kulcsok SHA-256 lenyomata (nyílt szövegű tárolás nélkül)
REVOKED_API_KEY_SHA256 = {
    "eb87f400e3f2736d7c49cd4b5b012a988101c64ca6e691709333e97c05509198",
}


class Settings(BaseSettings):
    mode: AppMode = Field(default=AppMode.DEMO, alias="PROXMONITOR_MODE")
    api_key: str = Field(default="titkos-mobil-api-kulcs-valtoztasd-meg", alias="PROXMONITOR_API_KEY")

    proxmox_host: Optional[str] = Field(default=None, alias="PROXMOX_HOST")
    proxmox_node: Optional[str] = Field(default="pve", alias="PROXMOX_NODE")
    proxmox_token_id: Optional[str] = Field(default=None, alias="PROXMOX_TOKEN_ID")
    proxmox_token_secret: Optional[str] = Field(default=None, alias="PROXMOX_TOKEN_SECRET")

    proxmox_verify_ssl: bool = Field(default=True, alias="PROXMOX_VERIFY_SSL")
    proxmox_ca_cert: Optional[str] = Field(default=None, alias="PROXMOX_CA_CERT")

    # Alapértelmezett 127.0.0.1 kötés a helyi/emulátoros elérés korlátozására
    host: str = Field(default="127.0.0.1", alias="PROXMONITOR_HOST")
    port: int = Field(default=8000, alias="PROXMONITOR_PORT")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def validate_live_config(self) -> None:
        """LIVE üzemmód biztonsági és konfigurációs feltételeinek ellenőrzése."""
        if self.mode == AppMode.LIVE:
            normalized_key = (self.api_key or "").strip()
            key_hash = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()
            if normalized_key in INSECURE_DEFAULT_API_KEYS or key_hash in REVOKED_API_KEY_SHA256:
                raise ValueError(
                    "A LIVE üzemmód nem használható üres vagy ismert alapértelmezett "
                    "PROXMONITOR_API_KEY értékkel! Állíts be egyedi, erős API-kulcsot a .env fájlban."
                )

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


settings = Settings()
