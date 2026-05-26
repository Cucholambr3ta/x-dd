"""__main__.py — Entrypoint del MCP server.

Uso:
  python3 -m xdd-mcp-server            # stdio mode (default)
  python3 -m xdd-mcp-server --check    # smoke test (lista tools y exit)
  python3 -m xdd-mcp-server --version
  python3 -m xdd-mcp-server --help
"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .server import serve_stdio
from .tools import TOOLS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="xdd-mcp-server",
                                     description="MCP server propio de X-DD.")
    parser.add_argument("-v", "--version", action="version",
                        version=f"xdd-mcp-server v{__version__}")
    parser.add_argument("--check", action="store_true",
                        help="Smoke test: lista tools como JSON y sale.")
    parser.add_argument("--transport", choices=["stdio"], default="stdio",
                        help="Transport (sólo stdio en v0.1.0).")
    args = parser.parse_args(argv)

    if args.check:
        out = {
            "server": "xdd-mcp-server",
            "version": __version__,
            "transport": "stdio",
            "tools": [t for t in TOOLS],
        }
        print(json.dumps(out, indent=2))
        return 0

    return serve_stdio()


if __name__ == "__main__":
    sys.exit(main())
