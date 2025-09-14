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
    """Response model for task data.

    Attributes:
        id: Unique task identifier
        title: Task title
        description: Optional task description
        priority: Task priority level
        due_date: Task due date
        completed: Task completion status
    """
    id: tasks.TaskID
    title: tasks.TaskTitle
    description: tasks.TaskDescription | None = None
    priority: tasks.PrioEnum
    due_date: datetime
    completed: tasks.TaskCompleted


class PostTasksReq(BaseModel):
    """Request model for creating a new task.

    Attributes:
        title: Task title
        description: Optional task description
        priority: Task priority level
        due_date: Task due date
    """
    title: tasks.TaskTitle
    description: tasks.TaskDescription | None = None
    priority: tasks.PrioEnum
    due_date: datetime


class UpdateTaskReq(BaseModel):
    """Request model for updating an existing task.

    Attributes:
        title: New task title (optional)
        description: New task description (optional)
        priority: New task priority (optional)
        due_date: New due date (optional)
        completed: New completion status (optional)
    """
    title: tasks.TaskTitle | None = None
    description: tasks.TaskDescription | None = None
    priority: tasks.PrioEnum | None = None
    due_date: datetime | None = None
    completed: tasks.TaskCompleted | None = None


class DeleteTaskResp(BaseModel):
    """Response model for task deletion.

    Attributes:
        message: Confirmation message
    """
    message: str


@router.get("/health")
def health():
    """Health check endpoint.

    Returns:
        HTTP 200 OK response indicating the service is healthy
    """
    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK)


@router.post("/tasks", response_model=TaskResp)
def post_tasks(req: PostTasksReq, taskdb: tasks.TaskReadWriter = Depends(get_taskdb)):
    """Create a new task.

    Returns:
        The created task

    Raises:
        HTTPException: 409 if task with generated ID already exists
        HTTPException: 422 if request invalid
    """
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
def get_tasks(completed: bool | None = None, priority: tasks.PrioEnum | None = None, search: str | None = None, taskdb: tasks.TaskReader = Depends(get_taskdb)):
    """Get all tasks with optional filtering.

    Args:
        completed: Filter by completion status (optional)
        priority: Filter by priority level (optional)
        search: Search term to filter by title/description (optional)

    Returns:
        List of tasks matching the filter criteria
    """
    all_tasks = tasks.get_all_tasks(taskdb, completed, priority, search)
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
    """Get a specific task by ID.

    Returns:
        The requested task

    Raises:
        HTTPException: 404 if task not found
    """
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
    """Update an existing task.

    Returns:
        The updated task

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 422 if request invalid
    """
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
    """Delete a task by ID.

    Returns:
        Confirmation message
    """
    tasks.delete_task(taskdb, task_id)
    return DeleteTaskResp(message="Task deleted successfully.")
