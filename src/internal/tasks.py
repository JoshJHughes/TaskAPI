from pydantic import BaseModel
from datetime import datetime
from enum import IntEnum

type TaskTitle = str
type TaskDescription = str
type TaskID = int
type TaskCompleted = bool

class PrioEnum(IntEnum):
    High = 1
    Medium = 2
    Low = 3

class Task(BaseModel):
    id: TaskID
    title: TaskTitle
    description: TaskDescription | None
    priority: PrioEnum
    due_date: datetime
    completed: TaskCompleted = False
