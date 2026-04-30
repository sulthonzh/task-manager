from __future__ import annotations

import datetime
import time

from executor.registry import ExecutorRegistry
from logger import setup_logger
from models.task import Task
from models.user import QuotaExceededError, UserManager

logger = setup_logger(__name__)


class Scheduler:
    def __init__(
        self,
        user_manager: UserManager,
        registry: ExecutorRegistry,
        tasks: list[Task],
    ) -> None:
        self._user_manager = user_manager
        self._registry = registry
        self._tasks = tasks

    def tick(self, current_time: str | None = None) -> int:
        now = current_time or datetime.datetime.now().strftime("%H:%M")
        executed = 0
        skipped = 0

        for task in self._tasks:
            if not task.is_due(now):
                continue

            user = self._user_manager.get(task.user)
            if not user.can_execute():
                logger.warning(
                    "%s has exceeded quota, skipping task %s",
                    user.username,
                    task.id,
                )
                skipped += 1
                continue

            executor = self._registry.get(task.action)
            executor.execute(task, user)
            executed += 1

        if executed > 0 or skipped > 0:
            logger.info(
                "Executed %d tasks. %d tasks skipped (quota).",
                executed,
                skipped,
            )
        return executed

    def run(self, interval: int = 60) -> None:
        logger.info("Scheduler running with %d tasks", len(self._tasks))
        while True:
            self.tick()
            time.sleep(interval)
