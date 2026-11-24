from pathlib import Path

lines = Path(".env").read_text().splitlines()

not_secret_keys = {
    "ENV",
    "FRONTEND_URL",
    "TEXTING_SERVICE_MODE",
}
output = []

for line in lines:
    if not line.strip() or line.strip().startswith("#"):
        output.append(line)
        continue
    if "=" in line:
        key = line.split("=", 1)[0]
        variable_name = key.strip().removeprefix("export ").strip()
        if variable_name in not_secret_keys:
            output.append(line)
        else:
            output.append(f"{key}=")

Path(".env.example").write_text("\n".join(output) + "\n")
