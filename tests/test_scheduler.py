from executor.registry import ExecutorRegistry
from executor.strategies.backup import BackupExecutor
from executor.strategies.delete import DeleteExecutor
from executor.strategies.sync import SyncExecutor
from models.task import Task
from models.user import User, UserManager


class TestScheduler:
    def _make_scheduler(
        self,
        users: dict[str, int],
        tasks: list[Task],
    ):
        user_manager = UserManager()
        for name, quota in users.items():
            user_manager.get_or_create(name, quota=quota)

        registry = ExecutorRegistry()
        registry.register("sync", SyncExecutor)
        registry.register("backup", BackupExecutor)
        registry.register("delete", DeleteExecutor)

        from scheduler.scheduler import Scheduler

        return Scheduler(user_manager, registry, tasks)

    def test_tick_executes_due_tasks(self):
        tasks = [
            Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
        ]
        scheduler = self._make_scheduler({"alice": 3}, tasks)
        count = scheduler.tick(current_time="12:00")
        assert count == 1

    def test_tick_skips_non_due(self):
        tasks = [
            Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
        ]
        scheduler = self._make_scheduler({"alice": 3}, tasks)
        count = scheduler.tick(current_time="13:00")
        assert count == 0

    def test_tick_enforces_quota(self):
        tasks = [
            Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
            Task(user="alice", scheduled_time="12:00", action="backup", target="/data/y"),
        ]
        scheduler = self._make_scheduler({"alice": 1}, tasks)
        count = scheduler.tick(current_time="12:00")
        assert count == 1
        user = scheduler._user_manager.get("alice")
        assert user.executed == 1

    def test_tick_returns_count(self):
        tasks = [
            Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
            Task(user="bob", scheduled_time="12:00", action="backup", target="/srv/y"),
        ]
        scheduler = self._make_scheduler({"alice": 3, "bob": 5}, tasks)
        count = scheduler.tick(current_time="12:00")
        assert count == 2

    def test_tick_no_due_tasks(self):
        tasks = [
            Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
        ]
        scheduler = self._make_scheduler({"alice": 3}, tasks)
        count = scheduler.tick(current_time="13:00")
        assert count == 0

    def test_multiple_users_same_time(self):
        tasks = [
            Task(user="alice", scheduled_time="12:00", action="sync", target="/data/x"),
            Task(user="bob", scheduled_time="12:00", action="backup", target="/srv/y"),
        ]
        scheduler = self._make_scheduler({"alice": 3, "bob": 5}, tasks)
        count = scheduler.tick(current_time="12:00")
        assert count == 2
        assert scheduler._user_manager.get("alice").executed == 1
        assert scheduler._user_manager.get("bob").executed == 1
