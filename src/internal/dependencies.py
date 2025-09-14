from src.internal.taskdb import InMemoryTaskDB

_task_db = InMemoryTaskDB()

def get_taskdb() -> InMemoryTaskDB:
    return _task_db