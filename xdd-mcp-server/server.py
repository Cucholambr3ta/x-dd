"""server.py — MCP server JSON-RPC 2.0 sobre stdio (mínimo viable).

Implementa el subset de Model Context Protocol necesario para exponer las 6
tools de X-DD. Sin deps PyPI (stdlib pura, ADR-0003).

Spec: https://spec.modelcontextprotocol.io/
"""
from __future__ import annotations

import json
import sys
from typing import Any, Iterable

from . import __version__
from .tools import TOOLS

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "xdd-mcp-server"


def make_response(req_id: Any, result: Any = None, error: dict | None = None) -> dict:
    msg: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg


def make_error(code: int, message: str, data: Any = None) -> dict:
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return err


def handle_initialize(params: dict) -> dict:
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"tools": {}},
        "serverInfo": {"name": SERVER_NAME, "version": __version__},
    }


def handle_tools_list(_params: dict) -> dict:
    return {"tools": [TOOLS[t]["schema"] for t in TOOLS]}


def handle_tools_call(params: dict) -> dict:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name not in TOOLS:
        raise ValueError(f"Tool desconocida: {name}")
    fn = TOOLS[name]["fn"]
    try:
        result = fn(**arguments)
    except TypeError as e:
        raise ValueError(f"Argumentos inválidos para {name}: {e}")
    return {
        "content": [
            {"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}
        ],
        "isError": isinstance(result, dict) and result.get("ok") is False,
    }


METHODS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


def dispatch(message: dict) -> dict | None:
    """Dispatcher principal. Devuelve la respuesta o None si es notification."""
    method = message.get("method")
    params = message.get("params") or {}
    req_id = message.get("id")

    # Notifications (sin id) no responden.
    is_notification = req_id is None

    if method == "notifications/initialized":
        return None

    if method not in METHODS:
        if is_notification:
            return None
        return make_response(req_id, error=make_error(-32601, f"Método no soportado: {method}"))

    try:
        result = METHODS[method](params)
    except ValueError as e:
        return make_response(req_id, error=make_error(-32602, str(e)))
    except Exception as e:  # noqa: BLE001
        return make_response(req_id, error=make_error(-32603, f"Error interno: {e}"))

    if is_notification:
        return None
    return make_response(req_id, result=result)


def serve_stdio(stdin: Iterable[str] = None, stdout=None) -> int:
    """Loop principal: lee JSON por línea de stdin, escribe respuestas a stdout."""
    if stdin is None:
        stdin = sys.stdin
    if stdout is None:
        stdout = sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            err = make_response(None, error=make_error(-32700, f"Parse error: {e}"))
            stdout.write(json.dumps(err) + "\n")
            stdout.flush()
            continue
        resp = dispatch(msg)
        if resp is not None:
            stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0
