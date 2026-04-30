from config import DEFAULT_INTERVAL
from executor.registry import ExecutorRegistry
from executor.strategies.backup import BackupExecutor
from executor.strategies.delete import DeleteExecutor
from executor.strategies.sync import SyncExecutor
from logger import setup_logger
from models.task import Task
from models.user import UserManager
from scheduler.scheduler import Scheduler

logger = setup_logger(__name__)


def main():
    user_manager = UserManager()
    user_manager.get_or_create("alice", quota=3)
    user_manager.get_or_create("bob", quota=5)

    registry = ExecutorRegistry()
    registry.register("sync", SyncExecutor)
    registry.register("backup", BackupExecutor)
    registry.register("delete", DeleteExecutor)

    tasks = [
        Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
        Task(
            user="bob",
            scheduled_time="12:00",
            action="backup",
            target="/srv/y",
            params={"compress": True, "retention_days": 7},
        ),
        Task(user="alice", scheduled_time="12:00", action="delete", target="/tmp/z"),
    ]

    scheduler = Scheduler(user_manager, registry, tasks)
    logger.info("Scheduler starting with %d tasks", len(tasks))
    scheduler.run(interval=DEFAULT_INTERVAL)


if __name__ == "__main__":
    main()