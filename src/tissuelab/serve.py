"""Launch the TissueLab HTML UI (plain HTTP, no Streamlit websocket)."""

from __future__ import annotations

import os
import socket
import sys

from tissuelab.paths import DB_PATH, ROOT

PORT = 8501


def _dual_stack_socket(port: int) -> socket.socket:
    """One socket that accepts both 127.0.0.1 and ::1.

    Chrome resolves localhost to ::1 first. Cursor's port forward often uses
    127.0.0.1. uvicorn --host 0.0.0.0 is IPv4-only; --host :: is IPv6-only.
    """
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    except OSError:
        pass
    sock.bind(("::", port))
    return sock


def main() -> None:
    if not DB_PATH.exists():
        print(
            f"Missing {DB_PATH}. From the repo root run:\n"
            "  python -m tissuelab.load_database",
            file=sys.stderr,
        )
        raise SystemExit(1)
    os.environ.setdefault("PYTHONPATH", str(ROOT / "src"))
    os.chdir(ROOT)
    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    sock = _dual_stack_socket(PORT)
    print(f"TissueLab: http://127.0.0.1:{PORT}/  and  http://localhost:{PORT}/", flush=True)

    import uvicorn

    config = uvicorn.Config(
        "app.api:app",
        fd=sock.fileno(),
        log_level="info",
        proxy_headers=True,
    )
    raise SystemExit(uvicorn.Server(config).run())


if __name__ == "__main__":
    main()
