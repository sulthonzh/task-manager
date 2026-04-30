from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Task:
    user: str
    scheduled_time: str
    action: str
    target: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    params: dict[str, Any] = field(default_factory=dict)

    def is_due(self, current_time: str) -> bool:
        return self.scheduled_time == current_time

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user": self.user,
            "scheduled_time": self.scheduled_time,
            "action": self.action,
            "target": self.target,
            "params": dict(self.params),
        }
