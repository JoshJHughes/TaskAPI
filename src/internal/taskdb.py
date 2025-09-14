import datetime
import sqlite3

from src.internal.errors import NotFoundError
from src.internal.tasks import Task, TaskID, PrioEnum


class InMemoryTaskDB:
    def __init__(self):
        self._db: dict[TaskID, Task] = {}

    def post(self, task: Task) -> None:
        """Creates or updates a new task."""
        self._db[task.id] = task

    def get_all(self, completed: bool | None = None, priority: PrioEnum | None = None) -> list[Task]:
        """Get all tasks. Return empty list if no tasks exist"""
        tasks = list(self._db.values())
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        if priority is not None:
            tasks = [task for task in tasks if task.priority == priority]
        return tasks

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


def convert_task_to_sqlite(task: Task) -> dict:
    data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "due_date": task.due_date.isoformat(),
        "completed": int(task.completed)
    }
    return data

def convert_sqlite_to_task(row: tuple) -> Task:
    return Task(
        id=row[0],
        title=row[1],
        description=row[2],
        priority=PrioEnum(row[3]),
        due_date=datetime.datetime.fromisoformat(row[4]),
        completed=bool(row[5]),
    )

class SQLiteTaskDB:
    def __init__(self, db_path, table_name, check_same_thread = True):
        self._table_name = table_name
        self._db_path = db_path
        self._con = sqlite3.connect(self._db_path, check_same_thread=check_same_thread)
        self._cur = self._con.cursor()
        self._cur.execute(
            f"""CREATE TABLE IF NOT EXISTS {self._table_name}(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER NOT NULL CHECK(priority IN (1,2,3)),
            due_date TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)));
            """)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._con.close()

    def post(self, task: Task) -> None:
        """Creates or updates a new task."""
        data = convert_task_to_sqlite(task)
        self._cur.execute(f"""
            INSERT OR REPLACE INTO {self._table_name}(id,title,description,priority,due_date,completed) 
            VALUES (:id,:title,:description,:priority,:due_date,:completed)
        """, data)
        self._con.commit()

    def get_all(self, completed: bool | None = None, priority: PrioEnum | None = None) -> list[Task]:
        """Get all tasks. Return empty list if no tasks exist"""
        query = f"SELECT * FROM {self._table_name}"
        params = []
        conditions = []

        if completed is not None:
            conditions.append("completed = ?")
            params.append(completed)

        if priority is not None:
            conditions.append("priority = ?")
            params.append(int(priority))

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        res = self._cur.execute(query, params)
        rows = res.fetchall()
        return [convert_sqlite_to_task(row) for row in rows]

    def get_by_id(self, task_id: TaskID) -> Task:
        """Get a task by ID. Raises NotFoundError if task doesn't exist."""
        data = {
            "id": task_id
        }
        res = self._cur.execute(f"""
            SELECT * FROM {self._table_name} WHERE id=:id
        """, data)
        row = res.fetchone()
        if row is None:
            raise NotFoundError(f"task with id {task_id} not found")
        return convert_sqlite_to_task(row)

    def delete(self, task_id: TaskID) -> None:
        """Delete a task by ID. Does not error if ID missing"""
        data = {
            "id": task_id
        }
        self._cur.execute(f"""
            DELETE FROM {self._table_name} WHERE id=:id
        """, data)
        self._con.commit()
