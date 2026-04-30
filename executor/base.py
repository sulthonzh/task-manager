from __future__ import annotations

from abc import ABC, abstractmethod

from logger import setup_logger
from models.task import Task
from models.user import QuotaExceededError, User

logger = setup_logger(__name__)


class TaskExecutor(ABC):
    @abstractmethod
    def execute(self, task: Task, user: User) -> None:
        ...

    def _log_start(self, task: Task) -> None:
        logger.info(
            "Executing %s on %s for %s",
            task.action,
            task.target,
            task.user,
        )

    def _log_complete(self, task: Task) -> None:
        logger.info(
            "Completed %s on %s for %s",
            task.action,
            task.target,
            task.user,
        )

    def _validate(self, task: Task, user: User) -> None:
        if not user.can_execute():
            logger.warning(
                "%s has exceeded quota (%d/%d), skipping task %s",
                user.username,
                user.executed,
                user.quota,
                task.id,
            )
            raise QuotaExceededError(
                user.username, user.quota, user.executed
            )
