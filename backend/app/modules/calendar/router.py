from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from sqlalchemy import or_, and_
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

@router.get("/student/{student_profile_id}/lessons", response_model=list[schemas.LessonResponse])
async def get_student_lessons(
    student_profile_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these lessons."
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

@router.get("/instructor/{instructor_profile_id}/lessons", response_model=list[schemas.LessonResponse])
async def get_instructor_lessons(
    instructor_profile_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these lessons."
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

# --------------------------------------- c ud -------------------------------------------------------------------------


async def verify_calendar_write_access(token: str):
    user_info = await tools.get_user(token)
    if user_info.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can modify the calendar."
        )
    return user_info


def check_lesson_conflict(db: Session, instructor_id, student_id, start, end, ignore_id=None):
    # Check if times are valid
    if start >= end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")


    query = db.query(models.CaLessons).filter(
        or_(
            models.CaLessons.instructor_id == instructor_id,
            models.CaLessons.student_id == student_id
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
        person = "Instructor" if conflict.instructor_id == instructor_id else "Student"
        raise HTTPException(
            status_code=400,
            detail=f"Time conflict detected for the {person}."
        )


@router.post("/lessons", response_model=schemas.LessonResponse)
async def add_lesson(
        lesson_in: schemas.LessonCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):

    await verify_calendar_write_access(token)

    check_lesson_conflict(db, lesson_in.instructor_id, lesson_in.student_id, lesson_in.start_time, lesson_in.end_time)

    new_lesson = models.CaLessons(**lesson_in.model_dump())
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