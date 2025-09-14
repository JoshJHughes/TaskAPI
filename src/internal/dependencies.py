from src.internal.taskdb import InMemoryTaskDB, SQLiteTaskDB

# _task_db = InMemoryTaskDB()
_task_db = SQLiteTaskDB("taskdb.db", "tasks")

def get_taskdb() -> SQLiteTaskDB:
    return _task_db