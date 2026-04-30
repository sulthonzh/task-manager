from __future__ import annotations


class QuotaExceededError(Exception):
    def __init__(self, username: str, quota: int, executed: int) -> None:
        self.username = username
        self.quota = quota
        self.executed = executed
        super().__init__(
            f"User '{username}' exceeded quota: {executed}/{quota}"
        )


class User:
    def __init__(self, username: str, quota: int, executed: int = 0) -> None:
        self.username = username
        self.quota = quota
        self.executed = executed

    def can_execute(self) -> bool:
        return self.executed < self.quota

    def record_execution(self) -> None:
        if self.executed >= self.quota:
            raise QuotaExceededError(self.username, self.quota, self.executed)
        self.executed += 1

    def reset(self) -> None:
        self.executed = 0


class UserManager:
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def get_or_create(self, username: str, quota: int) -> User:
        if username not in self._users:
            self._users[username] = User(username=username, quota=quota)
        return self._users[username]

    def get(self, username: str) -> User:
        if username not in self._users:
            raise KeyError(f"User '{username}' not found")
        return self._users[username]

    def all(self) -> list[User]:
        return list(self._users.values())
