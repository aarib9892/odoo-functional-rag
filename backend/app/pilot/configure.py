"""Create local pilot credentials without changing existing provider/DB secrets."""
import os
from pathlib import Path
import secrets


def main():
    target = Path(__file__).resolve().parents[2] / ".env.pilot"
    access, admin = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    contents = (
        f'PILOT_ACCESS_KEYS={{"operations":"{access}"}}\n'
        f"PILOT_ADMIN_KEY={admin}\n"
        "PILOT_PUBLIC_ORIGIN=http://localhost:8000\n"
        "PILOT_SECURE_COOKIE=false\n"
    )
    try:
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print(f"Existing {target.name} preserved. Edit it to add or rotate pilot keys.")
        return
    with os.fdopen(fd, "w") as output:
        output.write(contents)
    print(f"Created {target} with private local access and operator keys.")
    print("Use the operations access key from this file to sign in. Keys were not printed.")


if __name__ == "__main__":
    main()
