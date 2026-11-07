import argparse
from pathlib import Path

from dotenv import load_dotenv
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Launch the restricted local Odoo pilot")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    backend = Path(__file__).resolve().parents[2]
    load_dotenv(backend / ".env")
    load_dotenv(backend / ".env.pilot")
    uvicorn.run("app.pilot.api:create_app", factory=True, host=args.host, port=args.port,
                workers=1, proxy_headers=False)


if __name__ == "__main__":
    main()
