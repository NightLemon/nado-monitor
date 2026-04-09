import os
import pytest
from fastapi.testclient import TestClient

# Set test env before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test_nado.db"
os.environ["API_KEY"] = "test-api-key"
os.environ["TOTP_SECRET"] = ""

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    """Drop and recreate all tables between tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


SAMPLE_PAYLOAD = {
    "machine_name": "test-machine",
    "os_type": "linux",
    "cpu_percent": 25.0,
    "memory_percent": 50.0,
    "memory_used_gb": 8.0,
    "memory_total_gb": 16.0,
    "disk_percent": 60.0,
    "disk_used_gb": 120.0,
    "disk_total_gb": 200.0,
    "processes": [],
    "token_usage": [],
    "session_status": [],
}
