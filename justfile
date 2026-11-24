
# List available commands
default:
    @just --list

# Get Supabase token
token:
    uv run python -m dev.get_token

# Run Ruff linter
lint:
    uv run ruff check . --fix
# Run Ruff formatter

format:
    uv run ruff format .
    
# Start FastAPI server
run:
    uv run uvicorn app.main:app --reload

# Start Cloudflare tunnel
tunnel:
    cloudflared tunnel --url http://localhost:8000

# Deploy with an optional commit message
deploy message="Update":
    ./dev/deploy.sh "{{message}}"

# Generate a secure API key
key:
    openssl rand -hex 32

# Generate an example .env file
env-example:
    uv run python -m dev.gen_env_example
