"""Launch the TissueLab Streamlit app from the repo root."""

from __future__ import annotations

import os
import subprocess
import sys

from tissuelab.paths import DB_PATH, ROOT


def main() -> None:
    app = ROOT / "app" / "streamlit_app.py"
    if not app.exists():
        print(f"Missing Streamlit app at {app}", file=sys.stderr)
        raise SystemExit(1)
    if not DB_PATH.exists():
        print(
            f"Missing {DB_PATH}. From the repo root run:\n"
            "  python -m tissuelab.load_database",
            file=sys.stderr,
        )
        raise SystemExit(1)
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    raise SystemExit(
        subprocess.call(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app),
                "--browser.gatherUsageStats",
                "false",
            ],
            cwd=ROOT,
            env=env,
        )
    )


if __name__ == "__main__":
    main()
