
# list available commands
default:
    @just --list

# get supabase token
token:
    uv run python -m dev.get_token

# run ruff linter
lint:
    uv run ruff check . --fix

# run ruff formatter
format:
    uv run ruff format .

# lint and format
check: lint format
    
# start fastapi server
run:
    uv run uvicorn app.main:app --reload

# start cloudflare tunnel
tunnel:
    cloudflared tunnel --url http://localhost:8000

# deploy with an optional commit message
deploy message="Update":
    ./dev/deploy.sh "{{message}}"

# generate a secure API key
key:
    openssl rand -hex 32

# generate an example .env file
env-example:
    uv run python -m dev.gen_env_example

# run automated tests
test:
    uv run python -m pytest