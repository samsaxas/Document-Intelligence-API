import pytest
from app.database import engine, Base
from app.models import db_models

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
