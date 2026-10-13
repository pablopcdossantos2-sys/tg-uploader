from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

APP_NAME = "TGUploader"
KEYRING_SERVICE = "TGUploader"
KEYRING_API_HASH_KEY = "telegram_api_hash"


def app_data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


CONFIG_PATH = app_data_dir() / "config.json"
SESSION_PATH = app_data_dir() / "telegram_session"


@dataclass
class AppConfig:
    api_id: str = ""
    phone: str = ""
    last_folder: str = ""
    recursive: bool = True
    theme: str = "System"


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return AppConfig()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        allowed = {field for field in AppConfig.__dataclass_fields__}
        return AppConfig(**{k: v for k, v in data.items() if k in allowed})
    except (OSError, json.JSONDecodeError, TypeError):
        return AppConfig()


def save_config(config: AppConfig) -> None:
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_api_hash() -> str:
    try:
        import keyring

        return keyring.get_password(KEYRING_SERVICE, KEYRING_API_HASH_KEY) or ""
    except Exception:
        return ""


def save_api_hash(api_hash: str) -> bool:
    try:
        import keyring

        if api_hash:
            keyring.set_password(KEYRING_SERVICE, KEYRING_API_HASH_KEY, api_hash)
        else:
            try:
                keyring.delete_password(KEYRING_SERVICE, KEYRING_API_HASH_KEY)
            except Exception:
                pass
        return True
    except Exception:
        return False
