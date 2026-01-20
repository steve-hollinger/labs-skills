# OAuth 2.1 and OIDC Implementation Patterns

## Pattern 1: FastAPI OAuth Integration

```python
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import secrets

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

oauth = OAuth()
oauth.register(
    name='provider',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    server_metadata_url='https://provider.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.provider.authorize_redirect(request, redirect_uri)

@app.get('/callback')
async def auth_callback(request: Request):
    token = await oauth.provider.authorize_access_token(request)
    user = token.get('userinfo')
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')
```

## Pattern 2: Token Storage with Redis

```python
import json
from datetime import timedelta
from redis.asyncio import Redis
from cryptography.fernet import Fernet

class SecureTokenStore:
    def __init__(self, redis: Redis, encryption_key: bytes):
        self.redis = redis
        self.cipher = Fernet(encryption_key)

    async def store(self, user_id: str, tokens: dict, ttl: int = 86400):
        """Store encrypted tokens."""
        encrypted = self.cipher.encrypt(json.dumps(tokens).encode())
        await self.redis.setex(
            f"tokens:{user_id}",
            timedelta(seconds=ttl),
            encrypted,
        )

    async def retrieve(self, user_id: str) -> dict | None:
        """Retrieve and decrypt tokens."""
        encrypted = await self.redis.get(f"tokens:{user_id}")
        if not encrypted:
            return None
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted)

    async def delete(self, user_id: str):
        """Delete tokens on logout."""
        await self.redis.delete(f"tokens:{user_id}")
```

## Pattern 3: Automatic Token Refresh Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token_manager: TokenManager):
        super().__init__(app)
        self.token_manager = token_manager

    async def dispatch(self, request: Request, call_next):
        user_id = request.session.get('user_id')
        if user_id:
            try:
                # Refresh if needed
                access_token = await self.token_manager.get_valid_token(user_id)
                request.state.access_token = access_token
            except TokenExpiredError:
                # Clear session and redirect to login
                request.session.clear()
                return RedirectResponse('/login')

        return await call_next(request)
```

## Pattern 4: ID Token Validation Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def validate_id_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency for ID token validation."""
    try:
        validator = IDTokenValidator(oidc_config)
        user_info = validator.validate(
            credentials.credentials,
            nonce=None,  # Get from session if needed
        )
        return {
            'sub': user_info.subject,
            'email': user_info.email,
            'name': user_info.name,
        }
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@app.get('/api/profile')
async def get_profile(user: dict = Depends(validate_id_token)):
    return user
```

## Pattern 5: Multi-Provider Support

```python
from enum import Enum

class AuthProvider(str, Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"

PROVIDER_CONFIGS = {
    AuthProvider.GOOGLE: {
        'server_metadata_url': 'https://accounts.google.com/.well-known/openid-configuration',
        'client_kwargs': {'scope': 'openid profile email'},
    },
    AuthProvider.MICROSOFT: {
        'server_metadata_url': f'https://login.microsoftonline.com/{TENANT}/v2.0/.well-known/openid-configuration',
        'client_kwargs': {'scope': 'openid profile email'},
    },
    AuthProvider.GITHUB: {
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'client_kwargs': {'scope': 'read:user user:email'},
    },
}

oauth = OAuth()
for provider, config in PROVIDER_CONFIGS.items():
    oauth.register(
        name=provider.value,
        client_id=settings.get_client_id(provider),
        client_secret=settings.get_client_secret(provider),
        **config,
    )

@app.get('/login/{provider}')
async def login(request: Request, provider: AuthProvider):
    client = getattr(oauth, provider.value)
    redirect_uri = request.url_for('auth_callback', provider=provider.value)
    return await client.authorize_redirect(request, redirect_uri)
```

## Pattern 6: Logout with Token Revocation

```python
@app.get('/logout')
async def logout(request: Request):
    user_id = request.session.get('user_id')
    if user_id:
        # Revoke tokens at provider (if supported)
        tokens = await token_store.retrieve(user_id)
        if tokens and tokens.get('refresh_token'):
            await revoke_token(tokens['refresh_token'])

        # Clear local storage
        await token_store.delete(user_id)

    # Clear session
    request.session.clear()
    return RedirectResponse('/')

async def revoke_token(token: str):
    """Revoke token at the provider's revocation endpoint."""
    async with httpx.AsyncClient() as client:
        await client.post(
            settings.REVOCATION_ENDPOINT,
            data={
                'token': token,
                'client_id': settings.CLIENT_ID,
                'client_secret': settings.CLIENT_SECRET,
            },
        )
```

## Error Handling

```python
from enum import Enum

class OAuthError(str, Enum):
    INVALID_GRANT = "invalid_grant"  # Code/token expired or revoked
    INVALID_CLIENT = "invalid_client"  # Wrong client credentials
    INVALID_REQUEST = "invalid_request"  # Missing required parameter
    UNAUTHORIZED_CLIENT = "unauthorized_client"  # Client not allowed
    ACCESS_DENIED = "access_denied"  # User denied consent

def handle_oauth_error(error: str, description: str | None = None):
    """Handle OAuth error responses."""
    match error:
        case OAuthError.INVALID_GRANT:
            # Token expired/revoked - re-authenticate
            raise HTTPException(401, "Session expired, please login again")
        case OAuthError.ACCESS_DENIED:
            # User cancelled - redirect gracefully
            return RedirectResponse('/?error=cancelled')
        case _:
            # Log and show generic error
            logger.error(f"OAuth error: {error} - {description}")
            raise HTTPException(500, "Authentication failed")
```
