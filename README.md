# PMS Backend

A lightweight project management backend built with:

- Django + Graphene (GraphQL)
- PostgreSQL
- JWT authentication
- Multi-organization isolation (tenant context via `X-Organization-ID`)

This repository is designed for local development via Docker Compose.

## What’s included

- **Auth**: signup/login returning a JWT access token
- **Organizations**: users can belong to multiple orgs via memberships
- **Projects**: organization-scoped projects
- **Tasks**: organization-scoped tasks with status, optional assignee, and optional due dates
- **Comments**: task comments

## Prerequisites

- Docker
- Docker Compose (v2)

## Quickstart (Docker Compose)

From the repo root:

```bash
docker compose -f backend/docker-compose.yaml up --build
```

This will:

- Start Postgres on `localhost:5432`
- Start Django on `http://localhost:8000`
- Automatically run migrations on startup
- Automatically create a Django admin user (if configured)

## Admin user (auto-created)

The compose setup uses `backend/.env.example` by default. The backend container will create a superuser **once** (idempotent) if these are set:

- `DJANGO_ADMIN_EMAIL`
- `DJANGO_ADMIN_PASSWORD`

Default values in `.env.example`:

- Email: `admin@admin.com`
- Password: `admin`

Admin panel:

- `http://localhost:8000/admin/`

## Environment configuration

The compose file loads:

- `backend/.env.example`

For custom local settings, you can create your own file:

- Copy `backend/.env.example` -> `backend/.env`
- Then update `backend/docker-compose.yaml` to use `.env` instead of `.env.example` (recommended for real credentials).

Important DB variables:

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `DB_HOST`, `DB_PORT`

When running via Docker Compose, `DB_HOST` is overridden to `db` inside the container.

## GraphQL

GraphQL endpoint:

- `http://localhost:8000/graphql/`

Notes:

- Send JWT via `Authorization: Bearer <token>`.
- Most org-scoped operations require `X-Organization-ID: <organization_id>`.
- The `account` query returns the authenticated user plus org memberships without requiring `X-Organization-ID`.

## Common commands

Start services:

```bash
docker compose -f backend/docker-compose.yaml up --build
```

Stop services:

```bash
docker compose -f backend/docker-compose.yaml down
```

Reset DB volume (destructive):

```bash
docker compose -f backend/docker-compose.yaml down -v
```

View backend logs:

```bash
docker compose -f backend/docker-compose.yaml logs -f backend
```

## Troubleshooting

### `relation "accounts_user" does not exist`

This means migrations were not applied to the current database.

Fix:

- Ensure you started the **backend service** (not only `db`) using compose:

```bash
docker compose -f backend/docker-compose.yaml up --build
```

If you started only Postgres, run migrations by starting backend (it will run migrations on boot).
