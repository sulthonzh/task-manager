import pytest

from models.user import QuotaExceededError, User, UserManager


class TestUser:
    def test_user_creation(self):
        user = User(username="alice", quota=3)
        assert user.username == "alice"
        assert user.quota == 3
        assert user.executed == 0

    def test_can_execute_under_quota(self):
        user = User(username="alice", quota=3, executed=0)
        assert user.can_execute() is True

    def test_can_execute_at_quota(self):
        user = User(username="alice", quota=3, executed=3)
        assert user.can_execute() is False

    def test_can_execute_near_quota(self):
        user = User(username="alice", quota=3, executed=2)
        assert user.can_execute() is True

    def test_record_execution(self):
        user = User(username="alice", quota=3, executed=0)
        user.record_execution()
        assert user.executed == 1

    def test_record_execution_exceeds_quota(self):
        user = User(username="alice", quota=1, executed=1)
        with pytest.raises(QuotaExceededError) as exc_info:
            user.record_execution()
        assert exc_info.value.username == "alice"
        assert exc_info.value.quota == 1
        assert exc_info.value.executed == 1

    def test_reset(self):
        user = User(username="alice", quota=3, executed=2)
        user.reset()
        assert user.executed == 0


class TestUserManager:
    def test_get_or_create_new(self):
        manager = UserManager()
        user = manager.get_or_create("alice", quota=3)
        assert user.username == "alice"
        assert user.quota == 3

    def test_get_or_create_existing(self):
        manager = UserManager()
        user1 = manager.get_or_create("alice", quota=3)
        user1.record_execution()
        user2 = manager.get_or_create("alice", quota=5)
        assert user2 is user1
        assert user2.executed == 1
        assert user2.quota == 3

    def test_get_existing(self):
        manager = UserManager()
        manager.get_or_create("alice", quota=3)
        user = manager.get("alice")
        assert user.username == "alice"

    def test_get_missing(self):
        manager = UserManager()
        with pytest.raises(KeyError):
            manager.get("nonexistent")

    def test_all(self):
        manager = UserManager()
        manager.get_or_create("alice", quota=3)
        manager.get_or_create("bob", quota=5)
        all_users = manager.all()
        assert len(all_users) == 2
        usernames = {u.username for u in all_users}
        assert usernames == {"alice", "bob"}
