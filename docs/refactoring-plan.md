# Refactoring Plan

> Source: [`docs/prd.md`](./prd.md) · Current code: [`main.py`](../main.py)

---

## Overview

Refactor `main.py` from a 23-line procedural script into a class-based, modular architecture that supports multiple concurrent tasks per user, configurable parameters, structured logging, and extensible execution strategies.

---

## Target File Structure

```
.
├── main.py                  # Entry point (thin CLI / scheduler loop)
├── models/
│   ├── __init__.py
│   ├── user.py              # User + UserManager
│   └── task.py              # Task dataclass
├── executor/
│   ├── __init__.py
│   ├── base.py              # Abstract TaskExecutor
│   ├── registry.py          # Strategy registry / factory
│   └── strategies/
│       ├── __init__.py
│       ├── sync.py           # Sync action strategy
│       ├── backup.py         # Backup action strategy
│       └── delete.py         # Delete action strategy
├── scheduler/
│   ├── __init__.py
│   └── scheduler.py         # Simple time-based scheduler
├── config.py                # Default configuration & typing
├── logger.py                # Logging setup (logging module)
└── tests/
    ├── __init__.py
    ├── test_user.py
    ├── test_task.py
    ├── test_executor.py
    ├── test_scheduler.py
    └── test_strategies.py
```

---

## Phase 1 — Data Models

### Task 1.1: Create `models/user.py` — User Management & Quota Control

**Goal**: Encapsulate user state and quota enforcement in a class.

| Aspect | Detail |
|---|---|
| **Class** | `User` |
| **Fields** | `username: str`, `quota: int`, `executed: int` |
| **Methods** | `can_execute() -> bool` — returns `True` if `executed < quota` |
| | `record_execution() -> None` — increments `executed`, raises if over quota |
| | `reset() -> None` — resets `executed` to 0 |
| **Class** | `UserManager` |
| **Fields** | `_users: dict[str, User]` |
| **Methods** | `get_or_create(username: str, quota: int) -> User` |
| | `get(username: str) -> User` — raises `KeyError` if not found |
| | `all() -> list[User]` |

**Migration from `main.py`**:

```python
# BEFORE (global dict)
users = {
  'alice': {'quota': 3, 'executed': 0},
  'bob': {'quota': 5, 'executed': 0}
}

# AFTER (class instances)
manager = UserManager()
manager.get_or_create('alice', quota=3)
manager.get_or_create('bob', quota=5)
```

**Constraints**:
- `record_execution()` must raise a custom `QuotaExceededError` if called when quota is exhausted.
- Pure data logic — no I/O, no side effects.

---

### Task 1.2: Create `models/task.py` — Task Data Model

**Goal**: Define an immutable, typed task representation.

| Aspect | Detail |
|---|---|
| **Type** | `@dataclass(frozen=True)` |
| **Fields** | `id: str` (UUID), `user: str`, `scheduled_time: str` (`HH:MM`), `action: str`, `target: str`, `params: dict[str, Any]` (default `field(default_factory=dict)`) |
| **Methods** | `is_due(current_time: str) -> bool` — checks if `scheduled_time == current_time` |
| | `to_dict() -> dict` — serializable representation |

**Migration from `main.py`**:

```python
# BEFORE (raw dict)
tasks = [
  {'user': 'alice', 'time': '12:00', 'action': 'sync', 'target': '/data/x'},
]

# AFTER (dataclass)
task = Task(user='alice', scheduled_time='12:00', action='sync', target='/data/x')
```

**Constraints**:
- Frozen dataclass — tasks are immutable after creation.
- `params` dict supports arbitrary configurable parameters (PRD requirement).
- `id` auto-generated via `uuid.uuid4().hex[:8]` if not provided.

---

## Phase 2 — Executor System

### Task 2.1: Create `executor/base.py` — Abstract TaskExecutor

**Goal**: Define the interface all action strategies must implement.

| Aspect | Detail |
|---|---|
| **Class** | `TaskExecutor` (ABC) |
| **Abstract methods** | `execute(task: Task, user: User) -> None` |
| **Concrete helpers** | `_log_start(task) -> None` — logs execution start |
| | `_log_complete(task) -> None` — logs execution complete |
| | `_validate(task, user) -> None` — checks user quota, raises if exceeded |

**Constraints**:
- All concrete strategies inherit from `TaskExecutor`.
- `_validate` is called at the top of every `execute()` implementation.

---

### Task 2.2: Create `executor/registry.py` — Strategy Registry

**Goal**: Map action names to executor classes, enabling extensibility.

| Aspect | Detail |
|---|---|
| **Class** | `ExecutorRegistry` |
| **Fields** | `_registry: dict[str, type[TaskExecutor]]` |
| **Methods** | `register(action: str, executor_cls: type[TaskExecutor]) -> None` |
| | `get(action: str) -> TaskExecutor` — returns instance of registered executor |
| | `list_actions() -> list[str]` |

**Design**:

```python
registry = ExecutorRegistry()
registry.register('sync', SyncExecutor)
registry.register('backup', BackupExecutor)
registry.register('delete', DeleteExecutor)

executor = registry.get('sync')  # returns SyncExecutor instance
executor.execute(task, user)
```

**Constraints**:
- `get()` raises `KeyError` with helpful message if action not registered.

---

### Task 2.3: Create `executor/strategies/sync.py` — Sync Strategy

| Aspect | Detail |
|---|---|
| **Class** | `SyncExecutor(TaskExecutor)` |
| **execute logic** | Log "Syncing {target}", simulate work (placeholder), log completion |

---

### Task 2.4: Create `executor/strategies/backup.py` — Backup Strategy

| Aspect | Detail |
|---|---|
| **Class** | `BackupExecutor(TaskExecutor)` |
| **execute logic** | Log "Backing up {target}", simulate work, log completion |

---

### Task 2.5: Create `executor/strategies/delete.py` — Delete Strategy

| Aspect | Detail |
|---|---|
| **Class** | `DeleteExecutor(TaskExecutor)` |
| **execute logic** | Log "Deleting {target}", simulate work, log completion |

---

## Phase 3 — Scheduling System

### Task 3.1: Create `scheduler/scheduler.py` — Time-Based Scheduler

**Goal**: Orchestrate task checking and execution on a time-based loop.

| Aspect | Detail |
|---|---|
| **Class** | `Scheduler` |
| **Dependencies** | `UserManager`, `ExecutorRegistry`, list of `Task` |
| **Methods** | `__init__(user_manager, registry, tasks)` |
| | `tick(current_time: str or None = None) -> int` — runs one cycle, returns executed count |
| | `run(interval: int = 60) -> None` — blocking loop, calls `tick()` every `interval` seconds |

**tick logic**:
1. Get current time (or use `current_time` param for testing)
2. Filter tasks where `task.is_due(current_time)`
3. For each due task: get user -> check quota -> get executor -> execute -> record execution
4. Return executed count

**Migration from `main.py`**:

```python
# BEFORE
def run():
    now = datetime.datetime.now().strftime('%H:%M')
    for task in tasks:
        if task['time'] == now:
            # ... manual quota check + execution

# AFTER
scheduler = Scheduler(user_manager, registry, tasks)
scheduler.run(interval=60)
# or for testing:
scheduler.tick(current_time='12:00')
```

**Constraints**:
- `tick()` is pure logic (testable without `time.sleep`).
- `run()` handles the loop + `time.sleep`.
- Quota check happens BEFORE execution — no execution if quota exceeded.
- Each `tick()` logs summary: "Executed N tasks. M tasks skipped (quota)."

---

## Phase 4 — Logging & Configuration

### Task 4.1: Create `logger.py` — Structured Logging Setup

**Goal**: Centralized logging configuration using Python's `logging` module.

| Aspect | Detail |
|---|---|
| **Function** | `setup_logger(name: str, level: int = logging.INFO) -> logging.Logger` |
| **Format** | `%(asctime)s [%(levelname)s] %(name)s: %(message)s` |
| **Output** | Console (stdout) by default |
| **Usage** | Every module calls `logger = setup_logger(__name__)` |

**Replace all `print()` calls** in `main.py` with proper `logger.info()` / `logger.warning()` calls.

---

### Task 4.2: Create `config.py` — Default Configuration

**Goal**: Centralize default values and types.

| Aspect | Detail |
|---|---|
| **Contents** | `DEFAULT_QUOTA`, `DEFAULT_INTERVAL`, `SUPPORTED_ACTIONS`, `LOG_FORMAT` |
| **Types** | TypedDict or dataclass for config schema |
| **Loading** | Supports dict override for configurable parameters |

---

## Phase 5 — Entry Point Rewrite

### Task 5.1: Rewrite `main.py` — Thin Entry Point

**Goal**: Wire everything together with minimal code.

```python
"""Task Scheduler"""
from config import DEFAULT_INTERVAL
from models.user import UserManager
from models.task import Task
from executor.registry import ExecutorRegistry
from executor.strategies.sync import SyncExecutor
from executor.strategies.backup import BackupExecutor
from executor.strategies.delete import DeleteExecutor
from scheduler.scheduler import Scheduler
from logger import setup_logger

logger = setup_logger(__name__)


def main():
    # 1. Initialize user manager
    user_manager = UserManager()
    user_manager.get_or_create('alice', quota=3)
    user_manager.get_or_create('bob', quota=5)

    # 2. Register executors
    registry = ExecutorRegistry()
    registry.register('sync', SyncExecutor)
    registry.register('backup', BackupExecutor)
    registry.register('delete', DeleteExecutor)

    # 3. Define tasks (configurable via dict input)
    tasks = [
        Task(user='alice', scheduled_time='12:00', action='sync', target='/data/x'),
        Task(user='bob', scheduled_time='12:00', action='backup', target='/srv/y'),
        Task(user='alice', scheduled_time='12:00', action='delete', target='/tmp/z'),
    ]

    # 4. Run scheduler
    scheduler = Scheduler(user_manager, registry, tasks)
    logger.info("Scheduler starting with %d tasks", len(tasks))
    scheduler.run(interval=DEFAULT_INTERVAL)


if __name__ == '__main__':
    main()
```

**Constraints**:
- `main.py` should be < 40 lines (wiring only, no logic).
- All business logic lives in modules.

---

## Phase 6 — Tests

### Task 6.1: `tests/test_user.py` — User & UserManager Tests

| Test | Assertion |
|---|---|
| `test_user_creation` | Fields set correctly |
| `test_can_execute_under_quota` | Returns `True` when `executed < quota` |
| `test_can_execute_at_quota` | Returns `False` when `executed == quota` |
| `test_record_execution` | Increments `executed` |
| `test_record_execution_exceeds_quota` | Raises `QuotaExceededError` |
| `test_reset` | Sets `executed` back to 0 |
| `test_user_manager_get_or_create` | Creates new, returns existing on second call |
| `test_user_manager_get_missing` | Raises `KeyError` |

---

### Task 6.2: `tests/test_task.py` — Task Model Tests

| Test | Assertion |
|---|---|
| `test_task_creation` | Fields set correctly |
| `test_task_auto_id` | `id` is auto-generated |
| `test_task_frozen` | Raises `FrozenInstanceError` on mutation |
| `test_is_due_match` | Returns `True` when times match |
| `test_is_due_no_match` | Returns `False` when times differ |
| `test_task_params_default` | `params` defaults to `{}` |
| `test_task_custom_params` | `params` preserves custom values |

---

### Task 6.3: `tests/test_executor.py` — Executor Registry & Base Tests

| Test | Assertion |
|---|---|
| `test_registry_register_and_get` | Round-trip register -> get returns instance |
| `test_registry_get_unknown` | Raises `KeyError` |
| `test_registry_list_actions` | Returns all registered action names |
| `test_base_validate_quota_ok` | No exception when quota available |
| `test_base_validate_quota_exceeded` | Raises when quota exhausted |

---

### Task 6.4: `tests/test_scheduler.py` — Scheduler Tests

| Test | Assertion |
|---|---|
| `test_tick_executes_due_tasks` | Executes tasks matching current time |
| `test_tick_skips_non_due` | Does not execute tasks with different time |
| `test_tick_enforces_quota` | Skips tasks when user quota exhausted |
| `test_tick_returns_count` | Returns correct number of executed tasks |
| `test_tick_no_due_tasks` | Returns 0 when no tasks are due |
| `test_multiple_users_same_time` | Both users tasks execute independently |

---

### Task 6.5: `tests/test_strategies.py` — Strategy Tests

| Test | Assertion |
|---|---|
| `test_sync_executor` | Logs correct sync message |
| `test_backup_executor` | Logs correct backup message |
| `test_delete_executor` | Logs correct delete message |
| `test_strategy_calls_validate` | Quota check happens before execution |

---

## Phase 7 — Optional Extensions

### Task 7.1: Async Execution Version (Optional)

| Aspect | Detail |
|---|---|
| **File** | `scheduler/async_scheduler.py` |
| **Class** | `AsyncScheduler` |
| **Methods** | `async tick()`, `async run()` |
| **Change** | `asyncio.sleep` instead of `time.sleep`, `async def execute()` on strategies |
| **Note** | Only if time allows — not blocking for core delivery |

---

## Task Dependency Graph

```
Phase 1 (Models)
  +-- Task 1.1: User model
  +-- Task 1.2: Task model

Phase 2 (Executor)
  +-- Task 2.1: Base executor        (depends on 1.1, 1.2)
  +-- Task 2.2: Registry             (depends on 2.1)
  +-- Task 2.3: Sync strategy        (depends on 2.1)
  +-- Task 2.4: Backup strategy      (depends on 2.1)
  +-- Task 2.5: Delete strategy      (depends on 2.1)

Phase 3 (Scheduler)
  +-- Task 3.1: Scheduler            (depends on 1.x, 2.x)

Phase 4 (Infra)
  +-- Task 4.1: Logger               (independent)
  +-- Task 4.2: Config               (independent)

Phase 5 (Entry point)
  +-- Task 5.1: Rewrite main.py      (depends on all above)

Phase 6 (Tests)
  +-- Task 6.1-6.5: Tests            (depends on corresponding phase)

Phase 7 (Optional)
  +-- Task 7.1: Async version        (depends on Phase 3)
```

---

## Parallelization Opportunities

Tasks that can be done simultaneously:

- **Phase 1**: Tasks 1.1 + 1.2 in parallel (no dependency)
- **Phase 2**: Tasks 2.3 + 2.4 + 2.5 in parallel (all depend on 2.1 only)
- **Phase 4**: Tasks 4.1 + 4.2 in parallel (independent, can run alongside Phase 2)
- **Phase 6**: Tasks 6.1 + 6.2 in parallel (test models independently)

---

## Execution Order (Recommended)

```
1. Phase 4 (Infra: logger + config)          — independent foundation
2. Phase 1 (Models: user + task)             — parallel with Phase 4
3. Phase 2 (Executor: base -> registry + strategies)  — after Phase 1
4. Phase 3 (Scheduler)                       — after Phase 1 + 2
5. Phase 5 (main.py rewrite)                 — after all above
6. Phase 6 (Tests)                           — alongside each phase or after
7. Phase 7 (Async)                           — optional, after Phase 3
```

---

## Summary: 16 Tasks Across 7 Phases

| Phase | Tasks | New Files | Depends On |
|---|---|---|---|
| 1. Data Models | 2 | `models/user.py`, `models/task.py` | — |
| 2. Executor System | 4 | `executor/base.py`, `executor/registry.py`, 3 strategy files | Phase 1 |
| 3. Scheduler | 1 | `scheduler/scheduler.py` | Phase 1, 2 |
| 4. Logging & Config | 2 | `logger.py`, `config.py` | — |
| 5. Entry Point | 1 | `main.py` (rewrite) | Phase 1–4 |
| 6. Tests | 5 | 5 test files | Per-phase |
| 7. Optional Async | 1 | `scheduler/async_scheduler.py` | Phase 3 |
| **Total** | **16** | **~17 files** | |
