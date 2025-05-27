from typing import Sequence
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..schemas.assignment import AssignmentCreate, AssignmentOut


class AssignmentService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db.assignments

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _obj_id(id_: str | ObjectId) -> ObjectId:
        return id_ if isinstance(id_, ObjectId) else ObjectId(id_)

    # ── public API ───────────────────────────────────────────────────────
    async def create(self, payload: AssignmentCreate) -> AssignmentOut:
        doc = payload.model_dump(exclude_none=True)
        result = await self._col.insert_one(doc)
        return AssignmentOut(id=str(result.inserted_id), **doc)

    async def get(self, assignment_id: str) -> AssignmentOut | None:
        raw = await self._col.find_one({"_id": self._obj_id(assignment_id)})
        return (
            AssignmentOut(id=str(raw["_id"]), **raw)
            if raw
            else None
        )

    async def list_by_course(
        self, course_id: str, *, skip: int = 0, limit: int = 20
    ) -> Sequence[AssignmentOut]:
        cursor = (
            self._col.find({"course_id": course_id})
            .skip(skip)
            .limit(limit)
            .sort("due_date")
        )
        return [
            AssignmentOut(id=str(doc["_id"]), **doc) async for doc in cursor
        ]

    async def delete(self, assignment_id: str) -> bool:
        res = await self._col.delete_one({"_id": self._obj_id(assignment_id)})
        return res.deleted_count == 1
