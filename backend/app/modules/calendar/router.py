# --- PATH: app/modules/calendar/router.py ---
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List
from uuid import UUID

from app.database import get_db
from app import models, tools
from app.modules.calendar import schemas

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"]
)

# Points seamlessly to our central login handler on the Auth Microservice
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/auth/login")


# --- Permission Helpers ---

async def verify_calendar_write_access(token: str) -> dict:
    """Verifies with token helper that the caller is authorized to modify schedules."""
    user_info = await tools.get_user(token)
    if user_info.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can modify the calendar."
        )
    return user_info


def check_lesson_conflict(
        db: Session,
        instructor_profile_id: UUID,
        student_profile_id: UUID,
        start,
        end,
        ignore_id=None
):
    if start >= end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    query = db.query(models.CaLessons).filter(
        or_(
            models.CaLessons.instructor_id == instructor_profile_id,
            models.CaLessons.student_id == student_profile_id
        ),
        and_(
            models.CaLessons.start_time < end,
            models.CaLessons.end_time > start
        )
    )

    if ignore_id:
        query = query.filter(models.CaLessons.id != ignore_id)

    conflict = query.first()
    if conflict:
        person = "Instructor" if conflict.instructor_id == instructor_profile_id else "Student"
        raise HTTPException(
            status_code=400,
            detail=f"Time conflict detected for the {person}."
        )


# --- Endpoints ---

@router.get("/student/{student_profile_id}/lessons", response_model=List[schemas.LessonResponse])
async def get_student_lessons(
        student_profile_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Fetches upcoming lessons. Enforces ownership matching for student tokens."""
    user_info = await tools.get_user(token)
    user_role = user_info.get("role")
    user_id = UUID(user_info.get("id"))

    # Enforce data row visibility bounds
    if user_role not in ["admin", "instructor"]:
        # Look up what student profile row belongs to this auth account
        caller_profile = db.query(models.StProfiles).filter(models.StProfiles.user_id == user_id).first()
        if not caller_profile or caller_profile.id != student_profile_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have authorization to view these lessons."
            )

    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.student_id == student_profile_id)
        .all()
    )


@router.get("/instructor/{instructor_profile_id}/lessons", response_model=List[schemas.LessonResponse])
async def get_instructor_lessons(
        instructor_profile_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Fetches assigned instructor schedules. Enforces ownership matching for instructor tokens."""
    user_info = await tools.get_user(token)
    user_role = user_info.get("role")
    user_id = UUID(user_info.get("id"))

    # Enforce data row visibility bounds
    if user_role == "student":
        raise HTTPException(status_code=403, detail="Students cannot look up raw instructor logs directly.")

    if user_role == "instructor":
        caller_profile = db.query(models.InProfiles).filter(models.InProfiles.user_id == user_id).first()
        if not caller_profile or caller_profile.id != instructor_profile_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted to owner instructor or platform administrator."
            )

    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.instructor_id == instructor_profile_id)
        .all()
    )


@router.post("/lessons", response_model=schemas.LessonResponse)
async def add_lesson(
        lesson_in: schemas.LessonCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_calendar_write_access(token)

    # Validate references match secondary tables
    check_lesson_conflict(
        db,
        lesson_in.instructor_profile_id,
        lesson_in.student_profile_id,
        lesson_in.start_time,
        lesson_in.end_time
    )

    # Map the model keys precisely to maintain relational integrity
    new_lesson = models.CaLessons(
        instructor_id=lesson_in.instructor_profile_id,
        student_id=lesson_in.student_profile_id,
        start_time=lesson_in.start_time,
        end_time=lesson_in.end_time,
        status=lesson_in.status
    )

    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.id == new_lesson.id)
        .first()
    )


@router.put("/lessons/{lesson_id}", response_model=schemas.LessonResponse)
async def update_lesson(
        lesson_id: UUID,
        lesson_update: schemas.LessonUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_calendar_write_access(token)

    db_lesson = db.query(models.CaLessons).filter(models.CaLessons.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    new_start = lesson_update.start_time or db_lesson.start_time
    new_end = lesson_update.end_time or db_lesson.end_time

    if lesson_update.start_time or lesson_update.end_time:
        check_lesson_conflict(
            db,
            db_lesson.instructor_id,
            db_lesson.student_id,
            new_start,
            new_end,
            ignore_id=lesson_id
        )

    update_data = lesson_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lesson, key, value)

    db.commit()
    db.refresh(db_lesson)

    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.id == lesson_id)
        .first()
    )


@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
        lesson_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_calendar_write_access(token)

    db_lesson = db.query(models.CaLessons).filter(models.CaLessons.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(db_lesson)
    db.commit()
    return {"message": "Lesson successfully removed from the calendar"}