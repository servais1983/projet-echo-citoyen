"""Configuration des tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base, get_db, SessionLocal
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from datetime import timedelta
from app import crud, schemas
from app.models import User

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Crée le moteur de base de données pour les tests."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Crée une session de base de données pour les tests."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Crée un client de test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Crée un utilisateur de test."""
    # Supprimer l'utilisateur s'il existe déjà
    db_session.query(User).filter(User.email == "test@example.com").delete()
    db_session.commit()
    
    # Créer le nouvel utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    """Crée un token JWT pour les tests."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": test_user.email},
        expires_delta=access_token_expires
    )

@pytest.fixture
def db():
    """Crée une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 