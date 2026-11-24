"""Create a local signing key once, before running Django."""
import os
from pathlib import Path
import secrets

path = Path(__file__).resolve().with_name(".local-key")
try:
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
except FileExistsError:
    print("Local key already exists.")
else:
    with os.fdopen(fd, "w") as file:
        file.write(secrets.token_urlsafe(50))
    print("Local key created.")
