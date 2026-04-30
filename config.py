from dataclasses import dataclass
from typing import Any


DEFAULT_QUOTA: int = 5
DEFAULT_INTERVAL: int = 60
SUPPORTED_ACTIONS: tuple[str, ...] = ("sync", "backup", "delete")
LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


@dataclass(frozen=True)
class AppConfig:
    quota: int = DEFAULT_QUOTA
    interval: int = DEFAULT_INTERVAL
    actions: tuple[str, ...] = SUPPORTED_ACTIONS
    log_format: str = LOG_FORMAT

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        return cls(
            quota=data.get("quota", DEFAULT_QUOTA),
            interval=data.get("interval", DEFAULT_INTERVAL),
            actions=tuple(data.get("actions", SUPPORTED_ACTIONS)),
            log_format=data.get("log_format", LOG_FORMAT),
        )
