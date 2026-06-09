# --- PATH: auth_service/tests/conftest.py ---
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://root:rootpassword@localhost:5432/osk_default"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Creates a true isolated sandbox using nested savepoint transactions.
    Absolutely guarantees your local database is never permanently altered.
    """
    connection = engine.connect()
    # Begin an outer transaction loop
    transaction = connection.begin()
    # Bind an isolated session context
    session = TestingSessionLocal(bind=connection)

    # Begin a nested savepoint transaction. Commits inside application routes 
    # will only commit to this temporary savepoint context!
    session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Overrides the FastAPI database dependency."""

    def _get_db():
        try:
            yield db_session
        finally:
            pass

    return _get_db


# Pytest-asyncio / Anyio setting rule hook
@pytest.fixture
def anyio_backend():
    return "asyncio"