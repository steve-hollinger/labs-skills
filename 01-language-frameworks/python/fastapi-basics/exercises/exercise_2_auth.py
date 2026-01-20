"""Exercise 2: User Authentication

Implement JWT-based authentication for a FastAPI application.

Requirements:
1. Create user models:
   - UserCreate: username, email, password
   - UserLogin: username, password
   - UserResponse: id, username, email (no password!)
   - Token: access_token, token_type

2. Implement endpoints:
   - POST /auth/register - Register a new user
   - POST /auth/login - Login and get JWT token
   - GET /users/me - Get current user (protected)
   - PUT /users/me - Update current user (protected)

3. Implement authentication:
   - Hash passwords (use a simple hash for this exercise)
   - Create JWT tokens with expiration
   - Validate tokens in protected endpoints
   - Use OAuth2PasswordBearer for token extraction

4. Add error handling:
   - 401 for missing/invalid token
   - 409 for duplicate username/email
   - 400 for invalid credentials

Expected behavior:
    # Register
    POST /auth/register
    {"username": "alice", "email": "alice@example.com", "password": "secret"}
    -> 201 Created, {"id": 1, "username": "alice", "email": "alice@example.com"}

    # Login
    POST /auth/login
    {"username": "alice", "password": "secret"}
    -> 200 OK, {"access_token": "eyJ...", "token_type": "bearer"}

    # Get current user (with token)
    GET /users/me
    Headers: Authorization: Bearer eyJ...
    -> 200 OK, {"id": 1, "username": "alice", "email": "alice@example.com"}

Hints:
- Use OAuth2PasswordBearer from fastapi.security
- For JWT, you can use a simple dict encoded as base64 for this exercise
  (In production, use python-jose or PyJWT)
- Store users in a dictionary keyed by username
- Use Depends() to inject current user into protected routes
"""

import base64
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr


# TODO: Define your models here
class UserCreate(BaseModel):
    """Model for user registration."""
    pass


class UserResponse(BaseModel):
    """Model for user responses (no password)."""
    pass


class Token(BaseModel):
    """JWT token response."""
    pass


# Configuration
SECRET_KEY = "your-secret-key-here"
TOKEN_EXPIRE_MINUTES = 30

# Simulated database
users_db: dict = {}
next_id = 1

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# TODO: Implement helper functions
def hash_password(password: str) -> str:
    """Hash a password."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    pass


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT token."""
    pass


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    pass


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current authenticated user."""
    pass


# Create the app
app = FastAPI(title="Auth API")


# TODO: Implement your endpoints here
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    """Register a new user."""
    pass


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    pass


@app.get("/users/me")
def get_me(current_user = Depends(get_current_user)):
    """Get current user."""
    pass


def test_auth():
    """Test your authentication implementation."""
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test registration
    response = client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
    )
    print(f"Register: {response.status_code}")

    # TODO: Add more tests

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_auth()
