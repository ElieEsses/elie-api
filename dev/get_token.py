import os
import subprocess

import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("DB_URL") or ""
SUPABASE_KEY = os.getenv("DB_PUBLISHABLE_KEY") or ""
EMAIL = os.getenv("TOKEN_USER")
PASSWORD = os.getenv("TOKEN_PASSWORD")

response = requests.post(
    f"{SUPABASE_URL.rstrip('/')}/auth/v1/token",
    params={"grant_type": "password"},
    headers={
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
    },
    json={
        "email": EMAIL,
        "password": PASSWORD,
    },
    timeout=15,
)

if not response.ok:
    print("Status:", response.status_code)
    print("Error:", response.json())

response.raise_for_status()

access_token = response.json()["access_token"]

subprocess.run(
    ["pbcopy"],
    input=access_token,
    text=True,
    check=True,
)

print("Access token copied to clipboard.")
