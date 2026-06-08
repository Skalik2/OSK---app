from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_service.router import router as auth_router

app = FastAPI(
    title="OSK Dedicated Auth Microservice",
    description="Isolated Authentication System handling login and remote validation gates.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"status": "online", "service": "auth_microservice"}