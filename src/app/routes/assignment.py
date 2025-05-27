from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from .deps import get_db
from ..services.assignment import AssignmentService
from ..schemas.assignment import AssignmentCreate, AssignmentOut

router = APIRouter(
    prefix="/assignment",
    tags=["assignment"],
    responses={404: {"description": "Not found"}},
)


# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=AssignmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assignment",
)
async def create_assignment(
    payload: AssignmentCreate,
    svc: AssignmentService = Depends(lambda db=Depends(get_db): AssignmentService(db)),
):
    return await svc.create(payload)


# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/{assignment_id}",
    response_model=AssignmentOut,
    summary="Fetch a single assignment by id",
)
async def get_assignment(
    assignment_id: str,
    svc: AssignmentService = Depends(lambda db=Depends(get_db): AssignmentService(db)),
):
    doc = await svc.get(assignment_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return doc


# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/course/{course_id}",
    response_model=list[AssignmentOut],
    summary="List assignments for a course",
)
async def list_assignments(
    course_id: str,
    skip: int = 0,
    limit: int = 20,
    svc: AssignmentService = Depends(lambda db=Depends(get_db): AssignmentService(db)),
):
    items: Sequence[AssignmentOut] = await svc.list_by_course(
        course_id, skip=skip, limit=limit
    )
    return items


# ─────────────────────────────────────────────────────────────────────────────
@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assignment",
)
async def delete_assignment(
    assignment_id: str,
    svc: AssignmentService = Depends(lambda db=Depends(get_db): AssignmentService(db)),
):
    ok = await svc.delete(assignment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Assignment not found")
