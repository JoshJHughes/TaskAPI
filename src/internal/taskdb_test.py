import copy

import pytest
from datetime import datetime
from src.internal.tasks import Task, PrioEnum
from src.internal.taskdb import InMemoryTaskDB
from src.internal.errors import NotFoundError


@pytest.fixture()
def in_mem_task_db():
    return InMemoryTaskDB()

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
    def test_init(self, in_mem_task_db):
        """Initialisation should create an empty db"""
        assert len(in_mem_task_db._db) == 0

    def test_post_inserts(self, in_mem_task_db, sample_task):
        """Post should insert a new task"""
        in_mem_task_db.post(sample_task)

        assert in_mem_task_db.get_by_id(sample_task.id) == sample_task

    def test_post_updates(self, in_mem_task_db, sample_task):
        """Post should update task"""
        in_mem_task_db.post(sample_task)

        updated = copy.deepcopy(sample_task)
        new_title = "new title"
        updated.title = new_title
        assert sample_task.title != updated.title

        in_mem_task_db.post(updated)
        assert in_mem_task_db.get_by_id(sample_task.id).title == new_title

    def test_get_all_empty(self, in_mem_task_db):
        """Get all should return empty list for empty db"""
        assert len(in_mem_task_db.get_all()) == 0

    def test_get_all(self, in_mem_task_db, multiple_tasks):
        """Get all should return all tasks in db"""
        for task in multiple_tasks:
            in_mem_task_db.post(task)

        all_tasks = in_mem_task_db.get_all()
        assert all_tasks == multiple_tasks

    def test_get_by_id_missing(self, in_mem_task_db, sample_task):
        """Get by ID should raise NotFoundError if task missing"""
        with pytest.raises(NotFoundError):
            in_mem_task_db.get_by_id(sample_task.id)

    def test_get_by_id(self, in_mem_task_db, sample_task):
        """Get by ID should return correct task for existing ID"""
        in_mem_task_db.post(sample_task)
        assert in_mem_task_db.get_by_id(sample_task.id) == sample_task

    def test_delete_missing(self, in_mem_task_db, sample_task):
        """Delete should not error if task missing"""
        in_mem_task_db.delete(sample_task.id)

    def test_delete(self, in_mem_task_db, sample_task):
        """Delete should remove task from db"""
        in_mem_task_db.post(sample_task)
        assert in_mem_task_db.get_by_id(sample_task.id) == sample_task

        in_mem_task_db.delete(sample_task.id)
        with pytest.raises(NotFoundError):
            in_mem_task_db.get_by_id(sample_task.id)