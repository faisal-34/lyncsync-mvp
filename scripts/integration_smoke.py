import os
import sys
from pathlib import Path

def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from fastapi.testclient import TestClient
    from main import app

    load_dotenv(project_root / ".env")

    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit(
            "Missing GEMINI_API_KEY. Copy .env.example to .env and set your key first."
        )

    client = TestClient(app)
    response = client.post(
        "/orchestrate",
        json={"user_intent": "Onboard a new client named Acme Corp"},
    )

    print(f"HTTP {response.status_code}")
    print(response.json())

    if response.status_code != 200:
        raise SystemExit("Integration smoke test failed.")


if __name__ == "__main__":
    main()
