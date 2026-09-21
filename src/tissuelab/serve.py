"""Launch the TissueLab Predict UI in a browser (plain HTTP, no Streamlit websocket)."""

from __future__ import annotations

import os
import subprocess
import sys

from tissuelab.paths import DB_PATH, ROOT


def main() -> None:
    if not DB_PATH.exists():
        print(
            f"Missing {DB_PATH}. From the repo root run:\n"
            "  python -m tissuelab.load_database",
            file=sys.stderr,
        )
        raise SystemExit(1)
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(ROOT / "src"))
    print("TissueLab Predict: http://localhost:8501/", flush=True)
    raise SystemExit(
        subprocess.call(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.api:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8501",
            ],
            cwd=ROOT,
            env=env,
        )
    )


if __name__ == "__main__":
    main()
