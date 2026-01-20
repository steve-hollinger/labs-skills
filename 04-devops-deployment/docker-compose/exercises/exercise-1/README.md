# Exercise 1: Three-Tier Application

## Objective

Create a Docker Compose configuration for a three-tier application consisting of:
- Frontend (Nginx serving static files)
- API (Python/FastAPI)
- Database (PostgreSQL)

## Requirements

Your `docker-compose.yml` must:

1. **Define three services**: frontend, api, db
2. **Configure networking** so frontend can reach api, and api can reach db
3. **Set up volumes** for database persistence
4. **Configure environment variables** properly
5. **Expose appropriate ports** (frontend on 3000, api on 8000)

## Starting Files

- `frontend/` - Contains static HTML files and nginx config
- `api/` - Contains Python FastAPI application
- `docker-compose.yml` - Skeleton file to complete

## Steps

1. Review the provided application code in `frontend/` and `api/`

2. Complete the `docker-compose.yml` file:
   - Add the frontend service using nginx:alpine
   - Add the api service building from ./api
   - Add the db service using postgres:16-alpine
   - Configure volumes, networks, and environment variables

3. Start the services:
   ```bash
   docker compose up -d
   ```

4. Test the application:
   ```bash
   # Frontend should serve static page
   curl http://localhost:3000

   # API should respond
   curl http://localhost:8000/health

   # API should connect to database
   curl http://localhost:8000/db-status
   ```

## Hints

- Frontend needs to proxy API requests to the api service
- API needs DATABASE_URL environment variable
- Database needs POSTGRES_* environment variables
- Use named volumes for database persistence

## Success Criteria

- [ ] All three services start successfully
- [ ] Frontend serves static content on port 3000
- [ ] API responds on port 8000
- [ ] API can connect to database
- [ ] Data persists after `docker compose down` and `up`
