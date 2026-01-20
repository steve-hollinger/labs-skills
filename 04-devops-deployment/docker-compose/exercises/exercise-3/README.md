# Exercise 3: Environment Profiles

## Objective

Create a Docker Compose configuration that uses profiles to support different environments:
- **default**: Core services only (api, db)
- **debug**: Adds debugging tools (adminer, redis-commander)
- **worker**: Adds background workers
- **full**: All services

## Requirements

1. **Default profile**: Only essential services run without any flags
2. **Debug profile**: Adds database admin tools
3. **Worker profile**: Adds background processing
4. **Combine profiles**: Should work together (`--profile debug --profile worker`)

## Starting Point

The `docker-compose.yml` has all services but no profiles configured.

## Steps

1. Review the current `docker-compose.yml`

2. Add profiles to appropriate services:
   - `api` and `db`: No profile (always run)
   - `adminer` and `redis-commander`: `debug` profile
   - `worker`: `worker` profile
   - `cache`: No profile (needed by api)

3. Test different profiles:
   ```bash
   # Default - just api, db, cache
   docker compose up -d
   docker compose ps

   # With debug tools
   docker compose --profile debug up -d

   # With workers
   docker compose --profile worker up -d

   # Everything
   docker compose --profile debug --profile worker up -d
   ```

## Profile Usage

```yaml
services:
  adminer:
    image: adminer
    profiles:
      - debug  # Only runs when --profile debug is specified
```

## Success Criteria

- [ ] `docker compose up -d` starts only api, db, cache
- [ ] `--profile debug` adds adminer and redis-commander
- [ ] `--profile worker` adds worker service
- [ ] Profiles can be combined
- [ ] Core services work regardless of profiles
