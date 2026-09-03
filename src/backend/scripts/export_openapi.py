"""Export the authoritative FastAPI OpenAPI document for frontend type generation."""
import argparse
import json
from pathlib import Path

from app.main import app


DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[2]
    / "frontend"
    / "shared"
    / "api"
    / "openapi.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
