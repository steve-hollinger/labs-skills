# Common Patterns

## Overview

This document covers common patterns and best practices for building APIs with FastAPI.

## Pattern 1: CRUD API Structure

### When to Use

When building RESTful APIs with standard Create, Read, Update, Delete operations.

### Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/items", tags=["items"])

# Models
class ItemCreate(BaseModel):
    name: str
    price: float

class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

    model_config = {"from_attributes": True}

# Routes
@router.get("/", response_model=List[ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    return db.query(Item).offset(skip).limit(limit).all()

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db = Depends(get_db)):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    return db_item

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    return db_item

@router.patch("/{item_id}", response_model=ItemResponse)
def partial_update_item(item_id: int, item: ItemUpdate, db = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    return db_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
```

### Pitfalls to Avoid

- Don't return 200 for create operations (use 201)
- Don't forget to handle not-found cases
- Separate Create/Update models from Response models

## Pattern 2: Authentication with Dependencies

### When to Use

When you need to protect endpoints with authentication.

### Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user

# Login endpoint
@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@router.get("/users/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user
```

### Pitfalls to Avoid

- Never expose your secret key
- Always use HTTPS in production
- Consider token refresh mechanisms

## Pattern 3: Error Handling

### When to Use

Always. Consistent error handling improves API usability.

### Implementation

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
    field: str | None = None

# Custom exception
class AppError(Exception):
    def __init__(self, detail: str, error_code: str, status_code: int = 400):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code

# Exception handlers
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Usage
@router.get("/items/{item_id}")
def get_item(item_id: int):
    item = db.get(item_id)
    if not item:
        raise AppError(
            detail=f"Item {item_id} not found",
            error_code="ITEM_NOT_FOUND",
            status_code=404,
        )
    return item
```

### Pitfalls to Avoid

- Don't expose internal error details in production
- Always log errors before returning generic messages
- Use appropriate HTTP status codes

## Pattern 4: Background Tasks

### When to Use

When you need to perform operations after returning a response.

### Implementation

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Slow email sending operation
    import time
    time.sleep(5)
    print(f"Email sent to {email}")

def log_operation(operation: str, details: dict):
    # Log to external service
    logger.info(f"{operation}: {details}")

@router.post("/orders/")
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
):
    # Create order immediately
    db_order = create_order_in_db(order)

    # Queue background tasks
    background_tasks.add_task(
        send_email,
        order.customer_email,
        f"Order {db_order.id} confirmed!",
    )
    background_tasks.add_task(
        log_operation,
        "order_created",
        {"order_id": db_order.id, "amount": order.total},
    )

    return db_order  # Response returned immediately
```

### Pitfalls to Avoid

- Background tasks run in the same process
- Don't use for CPU-intensive work
- Consider Celery or similar for heavy tasks

## Pattern 5: File Uploads

### When to Use

When your API needs to accept file uploads.

### Implementation

```python
from fastapi import UploadFile, File, HTTPException
from typing import List
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")

    # Validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    # Save file
    file_path = UPLOAD_DIR / f"{uuid4()}{ext}"
    with open(file_path, "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "path": str(file_path)}

@router.post("/upload-multiple/")
async def upload_multiple(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        result = await upload_file(file)
        results.append(result)
    return results
```

### Pitfalls to Avoid

- Always validate file types and sizes
- Don't use original filenames (security risk)
- Consider streaming for large files

## Pattern 6: API Versioning

### When to Use

When you need to maintain multiple API versions.

### Implementation

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1 router
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

@v1_router.get("/items/")
def list_items_v1():
    return {"version": "v1", "items": [...]}

# Version 2 router with different structure
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v2_router.get("/items/")
def list_items_v2():
    return {
        "version": "v2",
        "data": {"items": [...]},
        "meta": {"total": 100},
    }

# Include both routers
app.include_router(v1_router)
app.include_router(v2_router)

# Alternative: Header-based versioning
@app.get("/items/")
def list_items(api_version: str = Header("1")):
    if api_version == "1":
        return {"version": "v1", "items": [...]}
    elif api_version == "2":
        return {"version": "v2", "data": {...}}
```

## Anti-Patterns

### Anti-Pattern 1: Blocking in Async Endpoints

Don't use blocking operations in async endpoints:

```python
# Bad - blocks the event loop
@app.get("/data")
async def get_data():
    result = requests.get("https://api.example.com")  # Blocking!
    return result.json()

# Good - use async client
@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        result = await client.get("https://api.example.com")
    return result.json()
```

### Anti-Pattern 2: Not Using Response Models

Always define response models:

```python
# Bad - untyped response
@app.get("/items/{id}")
def get_item(id: int):
    return {"id": id, "internal_field": "exposed"}  # Leaks data

# Good - controlled response
@app.get("/items/{id}", response_model=ItemResponse)
def get_item(id: int):
    item = get_from_db(id)
    return item  # Internal fields filtered out
```

### Anti-Pattern 3: Business Logic in Route Handlers

Keep route handlers thin:

```python
# Bad - business logic in handler
@app.post("/orders/")
def create_order(order: OrderCreate):
    # Lots of business logic here
    if order.total > 1000:
        apply_discount(order)
    inventory.reserve(order.items)
    payment.process(order)
    # ...more logic
    return order

# Good - separate service layer
@app.post("/orders/")
def create_order(order: OrderCreate, order_service = Depends(get_order_service)):
    return order_service.create(order)
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Standard CRUD API | CRUD API Structure |
| Protected endpoints | Authentication with Dependencies |
| Consistent error format | Error Handling |
| Post-response processing | Background Tasks |
| Image/document uploads | File Uploads |
| API evolution | API Versioning |
