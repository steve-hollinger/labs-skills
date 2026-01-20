---
name: implementing-oauth-oidc
description: Implements OAuth 2.1 and OpenID Connect authentication flows. Use when adding SSO, external auth providers, or identity federation.
---

# OAuth 2.1 And OIDC

## Quick Start
```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

oauth = OAuth()
oauth.register(
    name='provider',
    client_id=config('CLIENT_ID'),
    client_secret=config('CLIENT_SECRET'),
    authorize_url='https://provider.com/oauth/authorize',
    access_token_url='https://provider.com/oauth/token',
    client_kwargs={'scope': 'openid profile email'},
)

# Redirect to provider
@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.provider.authorize_redirect(request, redirect_uri)
```


## Key Points
- OAuth 2.1 consolidates best practices (PKCE required, no implicit flow)
- OIDC adds identity layer on top of OAuth 2.0
- Always validate ID token claims (iss, aud, exp, nonce)

## Common Mistakes
1. **Skipping PKCE** - Required in OAuth 2.1 for all clients
2. **Not validating state parameter** - CSRF vulnerability
3. **Storing tokens insecurely** - Use httpOnly cookies or secure storage

## More Detail
- [docs/concepts.md](docs/concepts.md) - OAuth 2.1 vs 2.0, OIDC flows
- [docs/patterns.md](docs/patterns.md) - Full implementation patterns
