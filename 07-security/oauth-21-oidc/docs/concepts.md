# OAuth 2.1 and OpenID Connect Concepts

## OAuth 2.1 Overview

OAuth 2.1 consolidates OAuth 2.0 best practices into a single specification:

- **PKCE Required**: All clients must use Proof Key for Code Exchange
- **No Implicit Flow**: Removed due to security concerns
- **No Password Grant**: Resource Owner Password Credentials removed
- **Refresh Token Rotation**: Recommended for all clients

## Key Components

### Roles

| Role | Description |
|------|-------------|
| Resource Owner | The user who owns the data |
| Client | Your application requesting access |
| Authorization Server | Issues tokens (e.g., Auth0, Okta) |
| Resource Server | API holding protected resources |

### Tokens

| Token | Purpose | Lifetime |
|-------|---------|----------|
| Access Token | API authorization | Minutes to hours |
| Refresh Token | Get new access tokens | Days to weeks |
| ID Token | User identity (OIDC) | Minutes |

## Authorization Code Flow with PKCE

```
┌──────────┐                              ┌─────────────────┐
│  Client  │                              │  Auth Server    │
└────┬─────┘                              └────────┬────────┘
     │                                             │
     │  1. Generate code_verifier + challenge      │
     │                                             │
     │  2. Redirect to /authorize                  │
     │     (code_challenge, state)                 │
     │─────────────────────────────────────────────>
     │                                             │
     │  3. User authenticates                      │
     │                                             │
     │  4. Redirect back with code + state         │
     │<─────────────────────────────────────────────
     │                                             │
     │  5. POST /token                             │
     │     (code, code_verifier)                   │
     │─────────────────────────────────────────────>
     │                                             │
     │  6. Return tokens                           │
     │<─────────────────────────────────────────────
```

## OpenID Connect

OIDC adds an identity layer on top of OAuth 2.0:

- **ID Token**: JWT containing user identity claims
- **UserInfo Endpoint**: Additional user information
- **Standard Scopes**: `openid`, `profile`, `email`
- **Discovery**: `/.well-known/openid-configuration`

### ID Token Claims

| Claim | Required | Description |
|-------|----------|-------------|
| `iss` | Yes | Issuer identifier |
| `sub` | Yes | Subject (user ID) |
| `aud` | Yes | Audience (client ID) |
| `exp` | Yes | Expiration time |
| `iat` | Yes | Issued at time |
| `nonce` | Conditional | Replay protection |
| `email` | No | User's email |
| `name` | No | User's name |

## Security Considerations

### State Parameter
- Random, unguessable value
- Prevents CSRF attacks
- Must be validated on callback

### Nonce Parameter
- Used in ID tokens
- Prevents replay attacks
- Required for implicit/hybrid flows

### PKCE
- Prevents authorization code interception
- S256 method recommended (SHA256)
- Plain method only if S256 unsupported

## Common Providers

| Provider | Discovery URL |
|----------|--------------|
| Google | `https://accounts.google.com/.well-known/openid-configuration` |
| Microsoft | `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration` |
| Auth0 | `https://{domain}/.well-known/openid-configuration` |
| Okta | `https://{domain}/.well-known/openid-configuration` |
