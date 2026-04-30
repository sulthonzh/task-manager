import uuid

import pytest

from models.task import Task


class TestTask:
    def test_task_creation(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        assert task.user == "alice"
        assert task.scheduled_time == "12:00"
        assert task.action == "sync"
        assert task.target == "/data/x"
        assert task.params == {}

    def test_task_auto_id(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        assert len(task.id) == 8

    def test_task_custom_id(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
            id="custom1",
        )
        assert task.id == "custom1"

    def test_task_frozen(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        with pytest.raises(AttributeError):
            task.user = "bob"

    def test_is_due_match(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        assert task.is_due("12:00") is True

    def test_is_due_no_match(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        assert task.is_due("13:00") is False

    def test_task_params_default(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
        )
        assert task.params == {}

    def test_task_custom_params(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
            params={"verbose": True, "depth": 3},
        )
        assert task.params["verbose"] is True
        assert task.params["depth"] == 3

    def test_to_dict(self):
        task = Task(
            user="alice",
            scheduled_time="12:00",
            action="sync",
            target="/data/x",
            id="abc123",
            params={"key": "val"},
        )
        d = task.to_dict()
        assert d["user"] == "alice"
        assert d["id"] == "abc123"
        assert d["params"] == {"key": "val"}
