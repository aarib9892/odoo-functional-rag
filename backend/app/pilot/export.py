"""Download an authenticated operator review export without printing credentials."""
import argparse
import os
from pathlib import Path
import urllib.request

from dotenv import load_dotenv
from app.pilot.settings import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(ROOT / "backend/.env")
    load_dotenv(ROOT / "backend/.env.pilot")
    origin = os.environ.get("PILOT_PUBLIC_ORIGIN", "http://localhost:8000")
    key = os.environ.get("PILOT_ADMIN_KEY")
    if not key:
        parser.error("PILOT_ADMIN_KEY must be configured")
    request = urllib.request.Request(origin + "/api/admin/export", headers={"Authorization": "Bearer " + key})
    # Refuse redirects so the operator credential cannot be forwarded to another origin.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=30) as response:
        data = response.read()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(data)
    print("Saved operator export:", args.output)


if __name__ == "__main__":
    main()
