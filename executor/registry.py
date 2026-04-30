from __future__ import annotations

from executor.base import TaskExecutor
from models.task import Task
from models.user import User


class ExecutorRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, type[TaskExecutor]] = {}

    def register(
        self, action: str, executor_cls: type[TaskExecutor]
    ) -> None:
        self._registry[action] = executor_cls

    def get(self, action: str) -> TaskExecutor:
        if action not in self._registry:
            available = ", ".join(sorted(self._registry.keys()))
            raise KeyError(
                f"Unknown action '{action}'. Registered: [{available}]"
            )
        return self._registry[action]()

    def list_actions(self) -> list[str]:
        return sorted(self._registry.keys())
