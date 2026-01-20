"""Solution for Exercise 2: User Authentication

This is the reference solution for the authentication exercise.
"""

import base64
import hashlib
import json
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field


# Models
class UserCreate(BaseModel):
    """Model for user registration."""

    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Model for user updates."""

    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)


class UserResponse(BaseModel):
    """Model for user responses (no password)."""

    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


# Configuration
SECRET_KEY = "your-secret-key-here-make-it-long-and-random"
TOKEN_EXPIRE_MINUTES = 30

# Simulated database
users_db: dict[str, dict] = {}  # username -> user data
next_id = 1

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Helper functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    salted = f"{SECRET_KEY}{password}"
    return hashlib.sha256(salted.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT-like token (simplified for exercise)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire.isoformat()})

    # Simple encoding (use real JWT library in production)
    json_data = json.dumps(to_encode)
    encoded = base64.urlsafe_b64encode(json_data.encode()).decode()
    return encoded


def decode_token(token: str) -> dict | None:
    """Decode and validate a token."""
    try:
        json_data = base64.urlsafe_b64decode(token.encode()).decode()
        data = json.loads(json_data)

        # Check expiration
        exp = datetime.fromisoformat(data["exp"])
        if exp < datetime.utcnow():
            return None

        return data
    except Exception:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception

    return user


# Create the app
app = FastAPI(
    title="Auth API",
    description="JWT-based authentication API",
    version="1.0.0",
)


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    """Register a new user."""
    global next_id

    # Check for duplicate username
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    # Check for duplicate email
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    new_user = {
        "id": next_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "created_at": datetime.now(),
    }
    users_db[user.username] = new_user
    next_id += 1

    return new_user


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    user = users_db.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return Token(access_token=access_token)


@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user."""
    return current_user


@app.put("/users/me", response_model=UserResponse)
def update_me(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update current user."""
    username = current_user["username"]
    user = users_db[username]

    if user_update.email is not None:
        # Check for duplicate email
        for other_user in users_db.values():
            if other_user["username"] != username and other_user["email"] == user_update.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
        user["email"] = user_update.email

    if user_update.password is not None:
        user["hashed_password"] = hash_password(user_update.password)

    return user


def test_auth():
    """Test the authentication implementation."""
    global users_db, next_id
    users_db = {}
    next_id = 1

    client = TestClient(app)
    print("Testing Auth API...")

    # Test 1: Register a user
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )
    assert response.status_code == 201
    user = response.json()
    assert user["username"] == "alice"
    assert "password" not in user  # Password should not be in response
    print("  Test 1 passed: User registration")

    # Test 2: Duplicate username
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "secret123",
        },
    )
    assert response.status_code == 409
    print("  Test 2 passed: Duplicate username rejected")

    # Test 3: Duplicate email
    response = client.post(
        "/auth/register",
        json={
            "username": "alice2",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )
    assert response.status_code == 409
    print("  Test 3 passed: Duplicate email rejected")

    # Test 4: Login with correct credentials
    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "secret123"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]
    print("  Test 4 passed: Login successful")

    # Test 5: Login with wrong password
    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    print("  Test 5 passed: Wrong password rejected")

    # Test 6: Login with non-existent user
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "secret123"},
    )
    assert response.status_code == 401
    print("  Test 6 passed: Non-existent user rejected")

    # Test 7: Access protected endpoint with token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "alice"
    print("  Test 7 passed: Protected endpoint with valid token")

    # Test 8: Access protected endpoint without token
    response = client.get("/users/me")
    assert response.status_code == 401
    print("  Test 8 passed: Protected endpoint rejects missing token")

    # Test 9: Access protected endpoint with invalid token
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    print("  Test 9 passed: Protected endpoint rejects invalid token")

    # Test 10: Update user
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"email": "newalice@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newalice@example.com"
    print("  Test 10 passed: User update")

    # Test 11: Password validation (too short)
    response = client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422
    print("  Test 11 passed: Short password rejected")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_auth()
