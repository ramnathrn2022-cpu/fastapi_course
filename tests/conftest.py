import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from app.main import app
from app.config import settings
from app.database import Base, get_db
from app import models
from app.oauth2 import create_access_token

# Build dynamic URL for test database
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=settings.database_port,
    database=f"{settings.database_name}_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def session():
    # Clean slate schema recreation for each test run
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client):
    user_data = {"email": "testuser@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email": "testuser2@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token(data={"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(session, test_user, test_user2):
    posts_data = [
        {
            "title": "first post",
            "content": "first content",
            "owner_id": test_user['id']
        },
        {
            "title": "2nd post",
            "content": "2nd content",
            "owner_id": test_user['id']
        },
        {
            "title": "3rd post",
            "content": "3rd content",
            "owner_id": test_user2['id']
        }
    ]
    
    post_models = [models.Post(**p) for p in posts_data]
    session.add_all(post_models)
    session.commit()
    
    posts = session.query(models.Post).all()
    return posts
