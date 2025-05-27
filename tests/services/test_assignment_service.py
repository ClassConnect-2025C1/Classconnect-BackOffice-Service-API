import pytest
from bson import ObjectId
from unittest.mock import AsyncMock, Mock

from src.app.services.assignment import AssignmentService
from src.app.schemas.assignment import AssignmentCreate, AssignmentOut


@pytest.mark.asyncio
async def test_create_assignment_returns_dto_with_string_id():
    # fake Motor collection
    fake_db = Mock()
    fake_col = AsyncMock()
    fake_db.assignments = fake_col

    svc = AssignmentService(fake_db)

    payload = AssignmentCreate(
        course_id="CS101",
        title="HW 1",
        due_date="2025-06-01T23:59:00Z",
        max_points=100,
    )

    fake_col.insert_one.return_value = Mock(
        inserted_id=ObjectId("64aa1111aa1111aa1111aa11")
    )

    out: AssignmentOut = await svc.create(payload)

    fake_col.insert_one.assert_awaited_once_with(payload.model_dump(exclude_none=True))
    assert out.id == "64aa1111aa1111aa1111aa11"
    assert out.course_id == "CS101"
