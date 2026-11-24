from pathlib import Path

lines = Path(".env").read_text().splitlines()

not_secret_keys = [
    "ENV",
    "FRONTEND_URL",
    "TEXTING_SERVICE_MODE",
]
output = []

for line in lines:
    if not line.strip() or line.strip().startswith("#"):
        output.append(line)
    if any(line.startswith(key) for key in not_secret_keys):
        output.append(line)
    elif "=" in line:
        key = line.split("=", 1)[0]
        output.append(f"{key}=")

Path(".env.example.test").write_text("\n".join(output) + "\n")
