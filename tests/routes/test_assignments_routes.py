# tests/routes/test_assignments_routes.py
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.app.routes.assignment import router as assignments_router
from src.app.routes.deps import get_db
from src.app.schemas.assignment import AssignmentCreate, AssignmentOut


# ── in-memory replacement for AssignmentService ────────────────────────────
class StubService:
    def __init__(self, *_unused, **_unused_kw):
        self._mem: dict[str, dict] = {}

    async def create(self, p: AssignmentCreate) -> AssignmentOut:
        new_id = f"id{len(self._mem)+1}"
        self._mem[new_id] = p.model_dump()
        return AssignmentOut(id=new_id, **self._mem[new_id])

    async def get(self, assignment_id: str):
        data = self._mem.get(assignment_id)
        return AssignmentOut(id=assignment_id, **data) if data else None

    async def list_by_course(self, course_id: str, *, skip=0, limit=20):
        items = [
            AssignmentOut(id=k, **v)
            for k, v in self._mem.items()
            if v["course_id"] == course_id
        ]
        return items[skip : skip + limit]

    async def delete(self, assignment_id: str) -> bool:
        return self._mem.pop(assignment_id, None) is not None


# ── FastAPI app fixture ────────────────────────────────
@pytest.fixture()
def app(monkeypatch) -> FastAPI:
    app = FastAPI()
    app.include_router(assignments_router)

    class _DummyDB: ...
    app.dependency_overrides[get_db] = lambda: _DummyDB()

    stub = StubService()

    monkeypatch.setattr(
        "src.app.services.assignment.AssignmentService",
        lambda *_a, **_kw: stub,
        raising=True,
    )
    monkeypatch.setattr(
        "src.app.routes.assignment.AssignmentService",
        lambda *_a, **_kw: stub,
        raising=True,
    )

    return app


# ── happy-path test ────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_and_get_assignment(app: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        payload = {
            "course_id": "CS101",
            "title": "HW 1",
            "due_date": "2025-06-01T23:59:00Z",
            "max_points": 100,
        }

        res = await client.post("/assignment/", json=payload)
        assert res.status_code == 201
        created = res.json()

        res = await client.get(f"/assignment/{created['id']}")
        assert res.status_code == 200
        assert res.json() == created
