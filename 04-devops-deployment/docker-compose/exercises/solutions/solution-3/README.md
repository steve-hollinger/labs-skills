# Solution 3: Environment Profiles

## Key Points

### 1. Profile Configuration

Services without `profiles` always run:
```yaml
api:
  # No profiles key = always runs
```

Services with `profiles` only run when that profile is active:
```yaml
adminer:
  profiles:
    - debug  # Only runs with --profile debug
```

### 2. Profile Usage

```bash
# Default - api, db, cache only
docker compose up -d

# With debug tools
docker compose --profile debug up -d

# With workers
docker compose --profile worker up -d

# Multiple profiles
docker compose --profile debug --profile worker up -d
```

### 3. Profile Groups

| Profile | Services Added |
|---------|---------------|
| (none) | api, db, cache |
| debug | + adminer, redis-commander |
| worker | + worker |
| debug + worker | all services |

## Testing

```bash
# Test default (3 services)
docker compose up -d
docker compose ps
# Should show: api, db, cache

docker compose down

# Test debug profile (5 services)
docker compose --profile debug up -d
docker compose ps
# Should show: api, db, cache, adminer, redis-commander

docker compose down

# Test worker profile (4 services)
docker compose --profile worker up -d
docker compose ps
# Should show: api, db, cache, worker

docker compose down

# Test all profiles (6 services)
docker compose --profile debug --profile worker up -d
docker compose ps
# Should show: all services
```

## Use Cases

- **Development**: `--profile debug` for admin tools
- **Production**: No profiles, just core services
- **Background jobs**: `--profile worker`
- **Full local setup**: Both profiles

## Environment Variables Alternative

You can also set profiles via environment:
```bash
export COMPOSE_PROFILES=debug,worker
docker compose up -d
```
