from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from modules.student import schemas
import models, tools
from typing import List
import httpx
from uuid import UUID

router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/auth/login")


@router.post("/register_initial")
async def register_student_auth(email: str, password: str):
    registration_data = {
        "email": email,
        "password": password,
        "role": "student"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8001/auth/register", json=registration_data)

            if response.status_code == 400:
                raise HTTPException(status_code=400, detail="Email already registered")

            if response.status_code != 201:  # Microservice returns 201 on success
                raise HTTPException(status_code=500, detail="Auth service error")

            return response.json()

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service is down")


@router.post("/register_full")
async def register_student_profile(
        profile_data: schemas.StudentProfileCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)

    if user_info.get("role") != "student":
        raise HTTPException(status_code=403, detail="Role mismatch")

    user_id = UUID(user_info['id'])

    existing_profile = db.query(models.StProfiles).filter(models.StProfiles.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")

    new_profile = models.StProfiles(
        user_id=user_id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        phone=profile_data.phone
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {"message": "Profile created successfully", "student_profile_id": new_profile.id}


@router.get("/check_only_user_created")
async def check_registration_status(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)

    if user_info.get("role") != "student":
        raise HTTPException(status_code=403, detail="Role mismatch")

    user_id = UUID(user_info['id'])
    profile = db.query(models.StProfiles).filter(models.StProfiles.user_id == user_id).first()

    if profile:
        return {"in_between_phases": False, "message": "Full registration complete"}

    return {"in_between_phases": True, "message": "Auth created, profile missing"}


# --------------------- courses ----------------------------------------------------------------------------------------

async def verify_admin_or_instructor(token: str) -> dict:
    user_info = await tools.get_user(token)
    if user_info.get("role") not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted to instructors and administrators."
        )
    return user_info


async def verify_only_admin(token: str) -> dict:
    user_info = await tools.get_user(token)
    if user_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted entirely to administrators."
        )
    return user_info


@router.post("/courses/register", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
async def register_student_course(
        course_in: schemas.CourseCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_admin_or_instructor(token)

    student_profile = db.query(models.StProfiles).filter(
        models.StProfiles.id == course_in.student_profile_id
    ).first()

    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified student profile does not exist."
        )

    existing_course = db.query(models.StCourses).filter(
        models.StCourses.student_profile_id == course_in.student_profile_id,
        models.StCourses.category == course_in.category
    ).first()

    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This student is already registered for a category {course_in.category} course."
        )

    new_course = models.StCourses(
        student_profile_id=course_in.student_profile_id,
        category=course_in.category,
        required_hours=course_in.required_hours,
        completed_hours=0,
        payment_status="PENDING"
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/courses/my_all", response_model=List[schemas.CourseResponse])
async def get_my_courses(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    user_id = UUID(user_info.get("id"))

    student_profile = db.query(models.StProfiles).filter(models.StProfiles.user_id == user_id).first()

    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    return db.query(models.StCourses).filter(models.StCourses.student_profile_id == student_profile.id).all()


@router.get("/courses/profile/{student_profile_id}", response_model=List[schemas.CourseResponse])
async def get_courses_by_student_profile(
        student_profile_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    user_info = await tools.get_user(token)
    user_role = user_info.get("role")
    user_id = UUID(user_info.get("id"))

    student_profile = db.query(models.StProfiles).filter(models.StProfiles.id == student_profile_id).first()
    if not student_profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    if user_role not in ["admin", "instructor"] and user_id != student_profile.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these courses."
        )

    return db.query(models.StCourses).filter(models.StCourses.student_profile_id == student_profile.id).all()


@router.put("/courses/{course_id}/update_payment", response_model=schemas.CourseResponse)
async def update_course_payment(
        course_id: UUID,
        payment_update: schemas.CoursePaymentUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_admin_or_instructor(token)

    course = db.query(models.StCourses).filter(models.StCourses.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course registration not found.")

    course.payment_status = payment_update.payment_status
    db.commit()
    db.refresh(course)
    return course


@router.put("/courses/{course_id}/update_hours", response_model=schemas.CourseResponse)
async def update_course_hours(
        course_id: UUID,
        hours_update: schemas.CourseHoursUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_admin_or_instructor(token)

    course = db.query(models.StCourses).filter(models.StCourses.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course registration not found.")

    if hours_update.completed_hours > course.required_hours:
        raise HTTPException(status_code=400, detail="Completed hours cannot exceed required course hours.")

    course.completed_hours = hours_update.completed_hours
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(
        course_id: UUID,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    await verify_only_admin(token)

    course = db.query(models.StCourses).filter(models.StCourses.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course registration not found.")

    db.delete(course)
    db.commit()
    return {"message": "Course registration successfully purged by administrator."}