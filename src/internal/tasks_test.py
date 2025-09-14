import os
import tempfile

import pytest
from datetime import datetime
from unittest.mock import patch
from src.internal.tasks import (
    Task, CreateTaskReq, UpdateTaskReq, PrioEnum,
    create_task, get_all_tasks, get_task_by_id, update_task, delete_task
)
from src.internal.taskdb import InMemoryTaskDB, SQLiteTaskDB
from src.internal.errors import AlreadyExistsError, NotFoundError


@pytest.fixture(params=["inmemory", "sqlite"])
def task_db(request):
    """Fixture that provides both InMemoryTaskDB and SQLiteTaskDB instances"""
    if request.param == "inmemory":
        yield InMemoryTaskDB()
    elif request.param == "sqlite":
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()

        db = SQLiteTaskDB(temp_db.name, "tasks")
        yield db

        db.close()
        os.unlink(temp_db.name)


@pytest.fixture
def sample_task():
    """Fixture providing a sample task for testing."""
    return Task(
        id=123,
        title="Sample Task",
        description="This is a sample task",
        priority=PrioEnum.medium,
        due_date=datetime(2024, 1, 1, 12, 0, 0),
        completed=False
    )


@pytest.fixture
def create_task_req():
    """Fixture providing a sample CreateTaskReq."""
    return CreateTaskReq(
        title="New Task",
        description="A new task to create",
        priority=PrioEnum.high,
        due_date=datetime(2024, 2, 1, 10, 0, 0)
    )


class TestCreateTask:
    """Tests for create_task function."""

    @patch('src.internal.tasks.random.randint')
    def test_create_task_success(self, mock_randint, task_db, create_task_req):
        """Test successful task creation when ID is not in use."""
        mock_randint.return_value = 456

        result = create_task(task_db, create_task_req)

        assert result.id == 456
        assert result.title == "New Task"
        assert result.description == "A new task to create"
        assert result.priority == PrioEnum.high
        assert result.due_date == datetime(2024, 2, 1, 10, 0, 0)
        assert result.completed is False

        # Verify task was saved to database
        saved_task = task_db.get_by_id(456)
        assert saved_task == result

    @patch('src.internal.tasks.random.randint')
    def test_create_task_already_exists_error(self, mock_randint, task_db, create_task_req, sample_task):
        """Test AlreadyExistsError when task ID already exists."""
        mock_randint.return_value = 123
        # Pre-populate database with existing task
        task_db.post(sample_task)

        with pytest.raises(AlreadyExistsError, match="task with id 123 already exists"):
            create_task(task_db, create_task_req)

    def test_create_task_with_none_description(self, task_db):
        """Test creating task with None description."""
        req = CreateTaskReq(
            title="Task without description",
            description=None,
            priority=PrioEnum.low,
            due_date=datetime(2024, 3, 1, 9, 0, 0)
        )

        with patch('src.internal.tasks.random.randint', return_value=789):
            result = create_task(task_db, req)

        assert result.description is None
        assert result.title == "Task without description"


class TestGetAllTasks:
    """Tests for get_all_tasks function."""

    def test_get_all_tasks_empty_db(self, task_db):
        """Test getting all tasks from empty database returns empty list."""
        result = get_all_tasks(task_db, None)
        assert result == []
        assert isinstance(result, list)

    def test_get_all_tasks_with_tasks(self, task_db):
        """Test getting all tasks when tasks exist in database."""
        task1 = Task(
            id=1,
            title="Task 1",
            description="First task",
            priority=PrioEnum.high,
            due_date=datetime(2024, 1, 1),
            completed=False
        )
        task2 = Task(
            id=2,
            title="Task 2",
            description="Second task",
            priority=PrioEnum.low,
            due_date=datetime(2024, 1, 2),
            completed=True
        )

        task_db.post(task1)
        task_db.post(task2)

        result = get_all_tasks(task_db, None)

        assert len(result) == 2
        assert task1 in result
        assert task2 in result

    def test_get_all_tasks_completed_true(self, task_db):
        """Test getting all tasks with completed = true."""
        task1 = Task(
            id=1,
            title="Task 1",
            description="First task",
            priority=PrioEnum.high,
            due_date=datetime(2024, 1, 1),
            completed=False
        )
        task2 = Task(
            id=2,
            title="Task 2",
            description="Second task",
            priority=PrioEnum.low,
            due_date=datetime(2024, 1, 2),
            completed=True
        )

        task_db.post(task1)
        task_db.post(task2)

        result = get_all_tasks(task_db, True)

        assert len(result) == 1
        assert task2 in result

    def test_get_all_tasks_completed_false(self, task_db):
        """Test getting all tasks with completed = false."""
        task1 = Task(
            id=1,
            title="Task 1",
            description="First task",
            priority=PrioEnum.high,
            due_date=datetime(2024, 1, 1),
            completed=False
        )
        task2 = Task(
            id=2,
            title="Task 2",
            description="Second task",
            priority=PrioEnum.low,
            due_date=datetime(2024, 1, 2),
            completed=True
        )

        task_db.post(task1)
        task_db.post(task2)

        result = get_all_tasks(task_db, False)

        assert len(result) == 1
        assert task1 in result

    def test_get_all_tasks_priority(self, task_db):
        """Test getting all tasks with given priority."""
        task1 = Task(
            id=1,
            title="Task 1",
            description="First task",
            priority=PrioEnum.high,
            due_date=datetime(2024, 1, 1),
            completed=False
        )
        task2 = Task(
            id=2,
            title="Task 2",
            description="Second task",
            priority=PrioEnum.low,
            due_date=datetime(2024, 1, 2),
            completed=True
        )

        task_db.post(task1)
        task_db.post(task2)

        result = get_all_tasks(task_db, priority=PrioEnum.low)

        assert len(result) == 1
        assert task2 in result

    def test_get_all_tasks_search(self, task_db):
        """Test getting all tasks with given priority."""
        task1 = Task(
            id=1,
            title="Task 1",
            description="First task",
            priority=PrioEnum.high,
            due_date=datetime(2024, 1, 1),
            completed=False
        )
        task2 = Task(
            id=2,
            title="Task 2",
            description="Second task",
            priority=PrioEnum.low,
            due_date=datetime(2024, 1, 2),
            completed=True
        )

        task_db.post(task1)
        task_db.post(task2)

        result = get_all_tasks(task_db, search="task")
        assert len(result) == 2
        assert task1 in result
        assert task2 in result

        result = get_all_tasks(task_db, search="first")
        assert len(result) == 1
        assert task1 in result


class TestGetTaskById:
    """Tests for get_task_by_id function."""

    def test_get_task_by_id_exists(self, task_db, sample_task):
        """Test getting task by ID when task exists."""
        task_db.post(sample_task)

        result = get_task_by_id(task_db, 123)

        assert result == sample_task
        assert result.id == 123

    def test_get_task_by_id_not_found(self, task_db):
        """Test NotFoundError when task ID doesn't exist."""
        with pytest.raises(NotFoundError, match="task with id 999 not found"):
            get_task_by_id(task_db, 999)


class TestUpdateTask:
    """Tests for update_task function."""

    def test_update_task_success_partial_update(self, task_db, sample_task):
        """Test successful partial task update."""
        task_db.post(sample_task)

        update_req = UpdateTaskReq(
            id=123,
            title="Updated Title",
            description=None,
            priority=None,
            due_date=None,
            completed=None
        )

        result = update_task(task_db, update_req)

        assert result.id == 123
        assert result.title == "Updated Title"
        # Unchanged fields should remain the same
        assert result.description == "This is a sample task"
        assert result.priority == PrioEnum.medium
        assert result.due_date == datetime(2024, 1, 1, 12, 0, 0)
        assert result.completed is False

        # Verify update was persisted
        saved_task = task_db.get_by_id(123)
        assert saved_task.title == "Updated Title"

    def test_update_task_success_full_update(self, task_db, sample_task):
        """Test successful full task update."""
        task_db.post(sample_task)

        update_req = UpdateTaskReq(
            id=123,
            title="Completely Updated Task",
            description="New description",
            priority=PrioEnum.low,
            due_date=datetime(2024, 12, 31, 23, 59, 59),
            completed=True
        )

        result = update_task(task_db, update_req)

        assert result.id == 123
        assert result.title == "Completely Updated Task"
        assert result.description == "New description"
        assert result.priority == PrioEnum.low
        assert result.due_date == datetime(2024, 12, 31, 23, 59, 59)
        assert result.completed is True

    def test_update_task_not_found(self, task_db):
        """Test NotFoundError when trying to update non-existent task."""
        update_req = UpdateTaskReq(
            id=999,
            title="Updated Title",
            description=None,
            priority=None,
            due_date=None,
            completed=None
        )

        with pytest.raises(NotFoundError, match="task with id 999 not found"):
            update_task(task_db, update_req)

    def test_update_task_all_none_fields(self, task_db, sample_task):
        """Test update with all None fields (should not change anything)."""
        task_db.post(sample_task)
        original_task = sample_task.model_copy()

        update_req = UpdateTaskReq(
            id=123,
            title=None,
            description=None,
            priority=None,
            due_date=None,
            completed=None
        )

        result = update_task(task_db, update_req)

        # All fields should remain unchanged
        assert result.title == original_task.title
        assert result.description == original_task.description
        assert result.priority == original_task.priority
        assert result.due_date == original_task.due_date
        assert result.completed == original_task.completed


class TestDeleteTask:
    """Tests for delete_task function."""

    def test_delete_task_exists(self, task_db, sample_task):
        """Test successful deletion of existing task."""
        task_db.post(sample_task)

        # Verify task exists before deletion
        assert task_db.get_by_id(123) == sample_task

        delete_task(task_db, 123)

        # Verify task was deleted
        with pytest.raises(NotFoundError):
            task_db.get_by_id(123)

    def test_delete_task_not_exists(self, task_db):
        """Test deletion of non-existent task should succeed without error."""
        # Should not raise any exception
        delete_task(task_db, 999)

    def test_delete_task_empty_db(self, task_db):
        """Test deletion from empty database should succeed without error."""
        delete_task(task_db, 123)