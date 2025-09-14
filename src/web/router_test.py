from datetime import datetime

import pytest
import fastapi
from fastapi.testclient import TestClient

from src.internal.dependencies import get_taskdb
from src.internal.taskdb import InMemoryTaskDB
from src.internal.tasks import PrioEnum
from src.main import app
from src.web.router import PostTasksReq, UpdateTaskReq


class TestTaskAPI:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        test_db = InMemoryTaskDB()
        app.dependency_overrides[get_taskdb] = lambda: test_db
        self.test_db = test_db
        yield
        app.dependency_overrides.clear()

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def sample_post_req(self):
        return PostTasksReq(
            title="title",
            description="desc",
            priority=PrioEnum(1),
            due_date=datetime(2025,9,10,5,3,43)
        )

    def test_create_task_success(self, client: TestClient, sample_post_req):
        req = sample_post_req
        resp = client.post("/tasks", content=req.model_dump_json())

        assert resp.status_code == fastapi.status.HTTP_200_OK
        resp_data = resp.json()
        assert resp_data["title"] == req.title
        assert resp_data["description"] == req.description
        assert resp_data["priority"] == req.priority
        assert datetime.fromisoformat(resp_data["due_date"]) == req.due_date

    def test_create_task_success_no_desc(self, client: TestClient, sample_post_req):
        req = sample_post_req
        req.description = None
        resp = client.post("/tasks", content=req.model_dump_json())

        assert resp.status_code == fastapi.status.HTTP_200_OK
        resp_data = resp.json()
        assert resp_data["title"] == req.title
        assert resp_data["description"] is None
        assert resp_data["priority"] == req.priority
        assert datetime.fromisoformat(resp_data["due_date"]) == req.due_date

    def test_create_task_unprocessable(self, client: TestClient):
        req = {
            "title": 36
        }
        resp = client.post("/tasks", json=req)

        assert resp.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_all_tasks_empty_db(self, client: TestClient):
        resp = client.get("/tasks")

        assert resp.status_code == fastapi.status.HTTP_200_OK
        resp_data = resp.json()
        assert len(resp_data) == 0

    def test_get_all_tasks_success(self, client: TestClient, sample_post_req):
        req = sample_post_req
        resp1 = client.post("/tasks", content=req.model_dump_json())
        resp2 = client.post("/tasks", content=req.model_dump_json())
        assert resp1.status_code == fastapi.status.HTTP_200_OK
        assert resp2.status_code == fastapi.status.HTTP_200_OK

        resp = client.get("/tasks")
        assert resp.status_code == fastapi.status.HTTP_200_OK

        resp_data = resp.json()
        assert len(resp_data) == 2

    def test_get_task_by_id_success(self, client: TestClient, sample_post_req):
        req = sample_post_req
        post_resp = client.post("/tasks", content=req.model_dump_json())
        assert post_resp.status_code == fastapi.status.HTTP_200_OK
        post_resp_data = post_resp.json()
        task_id = post_resp_data["id"]

        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == fastapi.status.HTTP_200_OK
        resp_data = resp.json()
        assert resp_data == post_resp_data

    def test_get_task_by_id_missing(self, client: TestClient):
        task_id = 123

        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == fastapi.status.HTTP_404_NOT_FOUND

    def test_update_task_success(self, client: TestClient, sample_post_req):
        req = sample_post_req
        post_resp = client.post("/tasks", content=req.model_dump_json())
        assert post_resp.status_code == fastapi.status.HTTP_200_OK
        post_resp_data = post_resp.json()
        task_id = post_resp_data["id"]

        new_title = "new title"
        updated = UpdateTaskReq(
            title=new_title,
        )

        resp = client.put(f"/tasks/{task_id}", content=updated.model_dump_json())
        assert resp.status_code == fastapi.status.HTTP_200_OK
        resp_data = resp.json()

        assert post_resp_data["id"] == resp_data["id"]
        assert resp_data["title"] == new_title
        assert post_resp_data["description"] == resp_data["description"]
        assert post_resp_data["priority"] == resp_data["priority"]
        assert post_resp_data["due_date"] == resp_data["due_date"]
        assert post_resp_data["completed"] == resp_data["completed"]

    def test_update_task_missing(self, client: TestClient):
        task_id = 123

        new_title = "new title"
        updated = UpdateTaskReq(
            title=new_title,
        )

        resp = client.put(f"/tasks/{task_id}", content=updated.model_dump_json())
        assert resp.status_code == fastapi.status.HTTP_404_NOT_FOUND

    def test_delete_success(self, client: TestClient, sample_post_req):
        req = sample_post_req
        post_resp = client.post("/tasks", content=req.model_dump_json())
        assert post_resp.status_code == fastapi.status.HTTP_200_OK
        post_resp_data = post_resp.json()
        task_id = post_resp_data["id"]

        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == fastapi.status.HTTP_200_OK

        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == fastapi.status.HTTP_404_NOT_FOUND

    def test_delete_missing(self, client: TestClient):
        task_id = 123

        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == fastapi.status.HTTP_200_OK

        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == fastapi.status.HTTP_404_NOT_FOUND