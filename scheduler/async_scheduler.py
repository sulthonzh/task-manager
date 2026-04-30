from __future__ import annotations

import asyncio
import datetime

from executor.registry import ExecutorRegistry
from logger import setup_logger
from models.task import Task
from models.user import UserManager

logger = setup_logger(__name__)


class AsyncScheduler:
    def __init__(
        self,
        user_manager: UserManager,
        registry: ExecutorRegistry,
        tasks: list[Task],
    ) -> None:
        self._user_manager = user_manager
        self._registry = registry
        self._tasks = tasks

    async def tick(self, current_time: str | None = None) -> int:
        now = current_time or datetime.datetime.now().strftime("%H:%M")
        executed = 0
        skipped = 0

        async def _execute_task(task: Task) -> int:
            user = self._user_manager.get(task.user)
            if not user.can_execute():
                logger.warning(
                    "%s has exceeded quota, skipping task %s",
                    user.username,
                    task.id,
                )
                return 0
            executor = self._registry.get(task.action)
            await asyncio.to_thread(executor.execute, task, user)
            return 1

        due_tasks = [t for t in self._tasks if t.is_due(now)]
        if due_tasks:
            results = await asyncio.gather(
                *[_execute_task(t) for t in due_tasks]
            )
            executed = sum(results)
            skipped = len(due_tasks) - executed

        if executed > 0 or skipped > 0:
            logger.info(
                "Executed %d tasks. %d tasks skipped (quota).",
                executed,
                skipped,
            )
        return executed

    async def run(self, interval: int = 60) -> None:
        logger.info("Async scheduler running with %d tasks", len(self._tasks))
        while True:
            await self.tick()
            await asyncio.sleep(interval)
