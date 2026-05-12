from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.database import get_db
from app import models, tools
from app.modules.calendar import schemas
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"]
)

# --------------------------------------- branie danych ----------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
# --- UNIFIED GET FOR STUDENTS ---
@router.get("/student/{student_profile_id}/lessons", response_model=list[schemas.LessonResponse])
async def get_student_lessons(
    student_profile_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    # Authorization logic (Admin or self)
    if user_info['role'] != 'admin':
        # ... ownership check as implemented before ...
        pass

    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.student_id == student_profile_id)
        .all()
    )

# --- UNIFIED GET FOR INSTRUCTORS ---
@router.get("/instructor/{instructor_profile_id}/lessons", response_model=list[schemas.LessonResponse])
async def get_instructor_lessons(
    instructor_profile_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    # Authorization logic (Admin or self)
    if user_info['role'] != 'admin':
        # ... ownership check as implemented before ...
        pass

    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.instructor_id == instructor_profile_id)
        .all()
    )

# --------------------------------------- c ud -----------------------------------------------------------------

from sqlalchemy import or_, and_


# --- HELPER: PERMISSION CHECK ---
async def verify_calendar_write_access(token: str):
    user_info = await tools.get_user(token)
    if user_info.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can modify the calendar."
        )
    return user_info


# --- HELPER: CONFLICT CHECK ---
def check_lesson_conflict(db: Session, instructor_id, student_id, start, end, ignore_id=None):
    # Check if times are valid
    if start >= end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    # Query for overlapping lessons for either the instructor OR the student
    query = db.query(models.CaLessons).filter(
        or_(
            models.CaLessons.instructor_id == instructor_id,
            models.CaLessons.student_id == student_id
        ),
        # Overlap logic: (StartA < EndB) AND (EndA > StartB)
        and_(
            models.CaLessons.start_time < end,
            models.CaLessons.end_time > start
        )
    )

    if ignore_id:
        query = query.filter(models.CaLessons.id != ignore_id)

    conflict = query.first()
    if conflict:
        person = "Instructor" if conflict.instructor_id == instructor_id else "Student"
        raise HTTPException(
            status_code=400,
            detail=f"Time conflict detected for the {person}."
        )


# --- ADD LESSON ---
@router.post("/lessons", response_model=schemas.LessonResponse)
async def add_lesson(
        lesson_in: schemas.LessonCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Admin and Instructors can create lessons. Checks for schedule conflicts."""
    await verify_calendar_write_access(token)

    # 1. Conflict detection (Instructor or Student already busy)
    check_lesson_conflict(db, lesson_in.instructor_id, lesson_in.student_id, lesson_in.start_time, lesson_in.end_time)

    # 2. Create the record
    new_lesson = models.CaLessons(**lesson_in.model_dump())
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    # 3. Re-fetch with joinedloads so the unified response has instructor/student names
    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.id == new_lesson.id)
        .first()
    )


# --- MODIFY LESSON ---
@router.put("/lessons/{lesson_id}", response_model=schemas.LessonResponse)
async def update_lesson(
        lesson_id: UUID,
        lesson_update: schemas.LessonUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Admin and Instructors can modify lessons (times or status)."""
    await verify_calendar_write_access(token)

    db_lesson = db.query(models.CaLessons).filter(models.CaLessons.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # 1. If times are changing, validate they don't overlap with other existing lessons
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

    # 2. Apply updates (status, times, etc.)
    update_data = lesson_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lesson, key, value)

    db.commit()
    db.refresh(db_lesson)

    # 3. Return the unified object with joined info
    return (
        db.query(models.CaLessons)
        .options(
            joinedload(models.CaLessons.instructor),
            joinedload(models.CaLessons.student)
        )
        .filter(models.CaLessons.id == lesson_id)
        .first()
    )


# --- REMOVE LESSON ---
@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
        lesson_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Admin and Instructors can remove/cancel lessons."""
    await verify_calendar_write_access(token)

    db_lesson = db.query(models.CaLessons).filter(models.CaLessons.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(db_lesson)
    db.commit()
    return {"message": "Lesson successfully removed from the calendar"}