from src.internal.errors import NotFoundError
from src.internal.tasks import Task, TaskID


class InMemoryTaskDB:
    def __init__(self):
        self._db: dict[TaskID, Task] = {}

    def post(self, task: Task) -> None:
        """Creates or updates a new task."""
        self._db[task.id] = task

    def get_all(self) -> list[Task]:
        """Get all tasks. Return empty list if no tasks exist"""
        return list(self._db.values())

    def get_by_id(self, task_id: TaskID) -> Task:
        """Get a task by ID. Raises NotFoundError if task doesn't exist."""
        if task_id not in self._db:
            raise NotFoundError(f"task with id {task_id} not found")
        return self._db[task_id]

    def delete(self, task_id: TaskID) -> None:
        """Delete a task by ID. Does not error if ID missing"""
        try:
            del self._db[task_id]
        except KeyError:
            return
