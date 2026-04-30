import pytest

from executor.base import TaskExecutor
from executor.registry import ExecutorRegistry
from executor.strategies.backup import BackupExecutor
from executor.strategies.delete import DeleteExecutor
from executor.strategies.sync import SyncExecutor
from models.task import Task
from models.user import QuotaExceededError, User


class TestExecutorRegistry:
    def test_registry_register_and_get(self):
        registry = ExecutorRegistry()
        registry.register("sync", SyncExecutor)
        executor = registry.get("sync")
        assert isinstance(executor, SyncExecutor)

    def test_registry_get_returns_new_instance(self):
        registry = ExecutorRegistry()
        registry.register("sync", SyncExecutor)
        e1 = registry.get("sync")
        e2 = registry.get("sync")
        assert e1 is not e2

    def test_registry_get_unknown(self):
        registry = ExecutorRegistry()
        with pytest.raises(KeyError, match="Unknown action 'missing'"):
            registry.get("missing")

    def test_registry_list_actions(self):
        registry = ExecutorRegistry()
        registry.register("sync", SyncExecutor)
        registry.register("backup", BackupExecutor)
        registry.register("delete", DeleteExecutor)
        assert registry.list_actions() == ["backup", "delete", "sync"]


class TestTaskExecutorValidate:
    def test_validate_quota_ok(self):
        user = User(username="alice", quota=3, executed=0)
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        executor = SyncExecutor()
        executor._validate(task, user)

    def test_validate_quota_exceeded(self):
        user = User(username="alice", quota=1, executed=1)
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        executor = SyncExecutor()
        with pytest.raises(QuotaExceededError):
            executor._validate(task, user)
