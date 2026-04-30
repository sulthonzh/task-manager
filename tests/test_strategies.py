import logging

import pytest

from executor.strategies.backup import BackupExecutor
from executor.strategies.delete import DeleteExecutor
from executor.strategies.sync import SyncExecutor
from models.task import Task
from models.user import QuotaExceededError, User


class TestSyncExecutor:
    def test_sync_executor(self, caplog):
        user = User(username="alice", quota=3, executed=0)
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        executor = SyncExecutor()
        with caplog.at_level(logging.INFO):
            executor.execute(task, user)
        assert "Syncing /data/x" in caplog.text
        assert user.executed == 1


class TestBackupExecutor:
    def test_backup_executor(self, caplog):
        user = User(username="bob", quota=5, executed=0)
        task = Task(
            user="bob",
            scheduled_time="12:00",
            action="backup",
            target="/srv/y",
        )
        executor = BackupExecutor()
        with caplog.at_level(logging.INFO):
            executor.execute(task, user)
        assert "Backing up /srv/y" in caplog.text
        assert user.executed == 1


class TestDeleteExecutor:
    def test_delete_executor(self, caplog):
        user = User(username="alice", quota=3, executed=0)
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="delete",
            target="/tmp/z",
        )
        executor = DeleteExecutor()
        with caplog.at_level(logging.INFO):
            executor.execute(task, user)
        assert "Deleting /tmp/z" in caplog.text
        assert user.executed == 1


class TestStrategyValidate:
    def test_strategy_calls_validate(self):
        user = User(username="alice", quota=1, executed=1)
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        executor = SyncExecutor()
        with pytest.raises(QuotaExceededError):
            executor.execute(task, user)


class TestParamsInExecution:
    def test_params_logged_in_sync(self, caplog):
        user = User(username="alice", quota=3, executed=0)
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
            params={"force": True, "dry_run": False},
        )
        executor = SyncExecutor()
        with caplog.at_level(logging.INFO):
            executor.execute(task, user)
        assert "'force': True" in caplog.text
        assert user.executed == 1

    def test_no_params_logs_none(self, caplog):
        user = User(username="bob", quota=5, executed=0)
        task = Task(
            user="bob",
            scheduled_time="12:00",
            action="backup",
            target="/srv/y",
        )
        executor = BackupExecutor()
        with caplog.at_level(logging.INFO):
            executor.execute(task, user)
        assert "params: none" in caplog.text
        assert user.executed == 1
