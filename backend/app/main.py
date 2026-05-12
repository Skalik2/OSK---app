from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.student import router as student_router
from app.modules.auth import router as auth_router
from app.modules.instructor import router as instructor_router
from app.modules.calendar import router as calendar_router
# from app.modules.admin import router as admin_router

app = FastAPI(
    title="OSK Core API",
    description="Backend Modułowy Monolit dla Ośrodka Szkolenia Kierowców",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Podpinanie routerów pod główną instancję aplikacji
app.include_router(student_router.router)
app.include_router(auth_router.router)
app.include_router(instructor_router.router)
app.include_router(calendar_router.router)
# app.include_router(admin_router.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "OSK Core API działa poprawnie"}