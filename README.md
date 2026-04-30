# Task Manager

Task scheduling and execution system with quota control.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## Test

```bash
uv run pytest tests/ -v
```

## Architecture

```
models/          User management & Task data model
executor/        TaskExecutor ABC, registry, and strategy implementations
scheduler/       Sync and async schedulers
config.py        Default configuration
logger.py        Structured logging setup
main.py          Entry point (<40 lines)
```

## Extend

Add a new action strategy by subclassing `TaskExecutor`:

```python
from executor.base import TaskExecutor
from models.task import Task
from models.user import User

class MyExecutor(TaskExecutor):
    def execute(self, task: Task, user: User) -> None:
        self._validate(task, user)
        self._log_start(task)
        # your logic here
        self._log_complete(task)
        user.record_execution()
```

Then register it in `main.py`:

```python
registry.register("my_action", MyExecutor)
```
