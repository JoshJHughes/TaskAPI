import copy
import os
import tempfile

import pytest
from datetime import datetime
from src.internal.tasks import Task, PrioEnum
from src.internal.taskdb import InMemoryTaskDB, SQLiteTaskDB
from src.internal.errors import NotFoundError


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
    return Task(
        id=1,
        title="Test Task",
        description="A test task",
        priority=PrioEnum.medium,
        due_date=datetime(2024, 12, 31, 23, 59, 59),
        completed=False
    )

@pytest.fixture
def multiple_tasks():
    return [
        Task(
            id=1,
            title="Task 1",
            description="First task",
            priority=PrioEnum.high,
            due_date=datetime(2024, 12, 31),
            completed=False
        ),
        Task(
            id=2,
            title="Task 2",
            description="Second task",
            priority=PrioEnum.low,
            due_date=datetime(2024, 11, 30),
            completed=True
        ),
        Task(
            id=3,
            title="Task 3",
            description=None,
            priority=PrioEnum.medium,
            due_date=datetime(2024, 10, 15),
            completed=False
        )
    ]

class TestInMemoryDB:
    def test_init(self, task_db):
        """Initialisation should create an empty db"""
        assert len(task_db.get_all(None)) == 0

    def test_post_inserts(self, task_db, sample_task):
        """Post should insert a new task"""
        task_db.post(sample_task)

        assert task_db.get_by_id(sample_task.id) == sample_task

    def test_post_updates(self, task_db, sample_task):
        """Post should update task"""
        task_db.post(sample_task)

        updated = copy.deepcopy(sample_task)
        new_title = "new title"
        updated.title = new_title
        assert sample_task.title != updated.title

        task_db.post(updated)
        assert task_db.get_by_id(sample_task.id).title == new_title

    def test_get_all_empty(self, task_db):
        """Get all should return empty list for empty db"""
        assert len(task_db.get_all(None)) == 0

    def test_get_all(self, task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            task_db.post(task)

        all_tasks = task_db.get_all(None)
        assert all_tasks == multiple_tasks

    def test_get_all_completed_true(self, task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            task_db.post(task)

        all_tasks = task_db.get_all(completed=True)
        for task in all_tasks:
            assert task.completed == True

    def test_get_all_completed_false(self, task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            task_db.post(task)

        all_tasks = task_db.get_all(completed=False)
        for task in all_tasks:
            assert task.completed == False

    def test_get_all_priority(self, task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            task_db.post(task)

        all_tasks = task_db.get_all(priority=PrioEnum.medium)
        for task in all_tasks:
            assert task.priority == PrioEnum.medium

    def test_get_all_priority_and_completed(self, task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            task_db.post(task)

        all_tasks = task_db.get_all(priority=PrioEnum.high, completed=False)
        for task in all_tasks:
            assert task.priority == PrioEnum.high

    def test_get_all_search(self, task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            task_db.post(task)

        query = "task"
        all_tasks = task_db.get_all(search=query)
        assert len(all_tasks) == 3
        assert multiple_tasks[0] in all_tasks
        assert multiple_tasks[1] in all_tasks
        assert multiple_tasks[2] in all_tasks

        query = "first"
        all_tasks = task_db.get_all(search=query)
        assert len(all_tasks) == 1
        assert multiple_tasks[0] in all_tasks

    def test_get_by_id_missing(self, task_db, sample_task):
        """Get by ID should raise NotFoundError if task missing"""
        with pytest.raises(NotFoundError):
            task_db.get_by_id(sample_task.id)

    def test_get_by_id(self, task_db, sample_task):
        """Get by ID should return correct task for existing ID"""
        task_db.post(sample_task)
        assert task_db.get_by_id(sample_task.id) == sample_task

    def test_delete_missing(self, task_db, sample_task):
        """Delete should not error if task missing"""
        task_db.delete(sample_task.id)

    def test_delete(self, task_db, sample_task):
        """Delete should remove task from db"""
        task_db.post(sample_task)
        assert task_db.get_by_id(sample_task.id) == sample_task

        task_db.delete(sample_task.id)
        with pytest.raises(NotFoundError):
            task_db.get_by_id(sample_task.id)