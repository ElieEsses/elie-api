# Elie's APIs

My central FastAPI backend for personal projects. A growing collection of APIs, shared infrastructure, and integrations.

## Projects

- **Digital Library** — Book management, reading progress, notes, and NFC integration.
- **Water Reminders** — Automated SMS reminders using Textbelt.

Built with Python, FastAPI, Pydantic, SQLAlchemy, and PostgreSQL. Hosted on Railway.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [just](https://github.com/casey/just)

## Getting Started

Install dependencies:

```bash
uv sync --locked
```

Create a local environment file:

```bash
cp .env.example .env
```

Fill in the required credentials and configuration values.
See `.env.example` for descriptions of each variable.

Start the API:

```bash
just run
```

Swagger documentation is available at [localhost:8000/docs](http://localhost:8000/docs).

## Development Commands

Commands are defined in the `justfile`.

| Command | Description |
|---|---|
| `just run` | Start the development server |
| `just lint` | Run Ruff with automatic fixes |
| `just token` | Get a Supabase access token |
| `just tunnel` | Start a Cloudflare tunnel |
| `just deploy "message"` | Regenerate environment template, lint, commit, push, and deploy |
| `just key` | Generate a secure API key |
| `just env-example` | Duplicate .env file as .env.example without secrets|

Run `just --list` to see all commands.

## Project Structure

```text
app/
├── main.py
├── config.py
├── shared/
│   ├── auth.py
│   ├── database.py
│   └── logging.py
└── projects/
    ├── library/
    │   ├── api/
    │   ├── db/
    │   ├── models/
    │   ├── repositories/
    │   └── services/
    └── water/
        ├── api/
        ├── models/
        └── services/
```

Each project contains its own API routes, models, and business logic. Shared infrastructure lives in `app/shared/`.

New projects can be added under `app/projects/` as the backend grows.