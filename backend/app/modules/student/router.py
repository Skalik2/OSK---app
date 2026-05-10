from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(
    prefix="/student",
    tags=["Student"],
    responses={404: {"description": "Not found"}},
)

@router.get("/profile")
def get_student_profile(db: Session = Depends(get_db)):
    # dodać jwt w przyszłości do autoryzacji i pobierania danych konkretnego kursanta
    return {"message": "Dane profilu kursanta (mock)"}

@router.get("/progress")
def get_student_progress(db: Session = Depends(get_db)):
    return {"message": "Postępy kursanta: 10/30h (mock)"}