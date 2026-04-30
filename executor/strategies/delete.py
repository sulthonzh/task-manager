from __future__ import annotations

from executor.base import TaskExecutor
from logger import setup_logger
from models.task import Task
from models.user import User

logger = setup_logger(__name__)


class DeleteExecutor(TaskExecutor):
    def execute(self, task: Task, user: User) -> None:
        self._validate(task, user)
        self._log_start(task)
        logger.info(
            "Deleting %s with params: %s",
            task.target,
            task.params or "none",
        )
        self._log_complete(task)
        user.record_execution()
