from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

APP_NAME = "TGUploader"


def app_root_dir() -> Path:
    """Return the folder that owns the portable application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def app_data_dir() -> Path:
    """Return a persistent data folder beside the portable application."""
    path = app_root_dir() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


DATA_DIR = app_data_dir()
CONFIG_PATH = DATA_DIR / "config.json"
SECRETS_PATH = DATA_DIR / "secrets.json"
SESSION_PATH = DATA_DIR / "telegram_session"


@dataclass
class AppConfig:
    api_id: str = ""
    phone: str = ""
    last_folder: str = ""
    recursive: bool = True
    theme: str = "System"
    language: str = "pt-BR"
    skip_duplicates: bool = True


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp.replace(path)


def load_config() -> AppConfig:
    data = _read_json(CONFIG_PATH)
    allowed = {field for field in AppConfig.__dataclass_fields__}
    try:
        config = AppConfig(**{k: v for k, v in data.items() if k in allowed})
    except TypeError:
        return AppConfig()
    if config.language not in {"pt-BR", "en", "es"}:
        config.language = "pt-BR"
    if config.theme not in {"System", "Dark", "Light"}:
        config.theme = "System"
    return config


def save_config(config: AppConfig) -> None:
    _write_json(CONFIG_PATH, asdict(config))


def load_api_hash() -> str:
    value = _read_json(SECRETS_PATH).get("telegram_api_hash", "")
    return value if isinstance(value, str) else ""


def save_api_hash(api_hash: str) -> bool:
    try:
        if api_hash:
            _write_json(SECRETS_PATH, {"telegram_api_hash": api_hash})
        elif SECRETS_PATH.exists():
            SECRETS_PATH.unlink()
        return True
    except OSError:
        return False
