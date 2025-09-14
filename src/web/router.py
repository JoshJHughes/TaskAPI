import fastapi
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from src.internal.errors import AlreadyExistsError, NotFoundError
import src.internal.tasks as tasks
from typing import List
from src.internal.dependencies import get_taskdb


router = fastapi.APIRouter()


class TaskResp(BaseModel):
    id: tasks.TaskID
    title: tasks.TaskTitle
    description: tasks.TaskDescription | None = None
    priority: tasks.PrioEnum
    due_date: datetime
    completed: tasks.TaskCompleted


class PostTasksReq(BaseModel):
    title: tasks.TaskTitle
    description: tasks.TaskDescription | None = None
    priority: tasks.PrioEnum
    due_date: datetime


class UpdateTaskReq(BaseModel):
    title: tasks.TaskTitle | None = None
    description: tasks.TaskDescription | None = None
    priority: tasks.PrioEnum | None = None
    due_date: datetime | None = None
    completed: tasks.TaskCompleted | None = None


class DeleteTaskResp(BaseModel):
    message: str


@router.get("/health")
def health():
    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK)


@router.post("/tasks", response_model=TaskResp)
def post_tasks(req: PostTasksReq, taskdb: tasks.TaskReadWriter = Depends(get_taskdb)):
    try:
        create_req = tasks.CreateTaskReq(
            title=req.title,
            description=req.description,
            priority=req.priority,
            due_date=req.due_date
        )
        task = tasks.create_task(taskdb, create_req)
        return TaskResp(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            completed=task.completed
        )
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/tasks", response_model=List[TaskResp])
def get_tasks(taskdb: tasks.TaskReader = Depends(get_taskdb)):
    all_tasks = tasks.get_all_tasks(taskdb)
    return [
        TaskResp(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            completed=task.completed
        )
        for task in all_tasks
    ]


@router.get("/tasks/{task_id}", response_model=TaskResp)
def get_task(task_id: int, taskdb: tasks.TaskReader = Depends(get_taskdb)):
    try:
        task = tasks.get_task_by_id(taskdb, task_id)
        return TaskResp(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            completed=task.completed
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.put("/tasks/{task_id}", response_model=TaskResp)
def update_task(
        task_id: int,
        req: UpdateTaskReq,
        taskdb: tasks.TaskReadWriter = Depends(get_taskdb)
):
    try:
        update_req = tasks.UpdateTaskReq(
            id=task_id,
            title=req.title,
            description=req.description,
            priority=req.priority,
            due_date=req.due_date,
            completed=req.completed
        )
        task = tasks.update_task(taskdb, update_req)
        return TaskResp(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            completed=task.completed
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/tasks/{task_id}", response_model=DeleteTaskResp)
def delete_task(task_id: int, taskdb: tasks.TaskWriter = Depends(get_taskdb)):
    try:
        tasks.delete_task(taskdb, task_id)
        return DeleteTaskResp(message="Task deleted successfully.")
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
