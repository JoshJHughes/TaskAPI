import random
from pydantic import BaseModel
from datetime import datetime
from enum import IntEnum
from typing import Protocol
from src.internal.errors import AlreadyExistsError, NotFoundError

ID_MAX = 2147483647

type TaskTitle = str
type TaskDescription = str
type TaskID = int
type TaskCompleted = bool

class PrioEnum(IntEnum):
    high = 1
    medium = 2
    low = 3

class Task(BaseModel):
    id: TaskID
    title: TaskTitle
    description: TaskDescription | None
    priority: PrioEnum
    due_date: datetime
    completed: TaskCompleted = False

class CreateTaskReq(BaseModel):
    title: TaskTitle
    description: TaskDescription | None = None
    priority: PrioEnum
    due_date: datetime

class UpdateTaskReq(BaseModel):
    id: TaskID
    title: TaskTitle | None
    description: TaskDescription | None
    priority: PrioEnum | None
    due_date: datetime | None
    completed: TaskCompleted | None

class TaskReader(Protocol):
    def get_by_id(self, task_id: TaskID) -> Task:
        ...

    def get_all(self) -> list[Task]:
        ...

class TaskWriter(Protocol):
    def post(self, task: Task) -> None:
        ...

    def delete(self, task_id: TaskID) -> None:
        ...

class TaskReadWriter(TaskReader, TaskWriter, Protocol):
    ...

def create_task(db: TaskReadWriter, req: CreateTaskReq) -> Task:
    task_id = random.randint(0, ID_MAX)
    try:
        db.get_by_id(task_id)
        raise AlreadyExistsError(f"task with id {task_id} already exists")
    except NotFoundError:
        pass
    task = Task(
        id=task_id,
        title=req.title,
        description=req.description,
        priority=req.priority,
        due_date=req.due_date,
        completed=False
    )
    db.post(task)
    return task

def get_all_tasks(db: TaskReader) -> list[Task]:
    return db.get_all()

def get_task_by_id(db: TaskReader, task_id: TaskID) -> Task:
    return db.get_by_id(task_id)

def update_task(db: TaskReadWriter, req: UpdateTaskReq) -> Task:
    task = get_task_by_id(db, req.id)
    update_data = req.model_dump(exclude_none=True, exclude={"id"})
    updated = task.model_copy(update=update_data)
    db.post(updated)
    return updated

def delete_task(db: TaskWriter, task_id: TaskID) -> None:
    return db.delete(task_id)
