#!/usr/bin/env python3
"""xdd-provider.py — Abstracción de proveedor LLM para X-DD (puerto hexagonal).

Portado del piloto agentix. Cubre el hueco: X-DD no tenía capa para ejecutar/
testear flujos de agentes SIN red ni tokens. El `MockProvider` determinista
permite que xdd-flow.py y el eval-harness validen ejecución reproducible.

Componentes:
  ProviderPort      — Protocol `complete(prompt, system) -> str` (structural typing).
  MockProvider      — determinista, sin I/O; registra `.calls` para aserciones.
  AnthropicProvider — adapter real (lazy-import de `anthropic`, dep opcional).
  get_provider()    — factory: respeta XDD_PROVIDER_MOCK / --mock; sin red por defecto.

Diseño: stdlib-only en el path de tests (anthropic es lazy y opcional).
Relación: xdd-router.py SUGIERE provider/model; este módulo lo INSTANCIA.

Uso CLI:
  xdd-provider.py --self-test        # verifica MockProvider determinista (sin red)
  xdd-provider.py --complete "hola"  # usa mock por defecto; real si XDD_PROVIDER_MOCK=0 + key
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Protocol, runtime_checkable

__version__ = "0.1.0-dev"


@runtime_checkable
class ProviderPort(Protocol):
    """Puerto de proveedor LLM (hexagonal). Implementa `complete` para ser provider."""

    def complete(self, prompt: str, system: str | None = None) -> str: ...


class MockProvider:
    """Provider determinista sin red. Devuelve respuesta mapeada, default o eco.

    Pensado para tests y para que xdd-flow.py ejecute pipelines reproducibles
    sin consumir tokens. `calls` registra cada invocación para aserciones.
    """

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        default: str | None = None,
    ):
        self.responses = dict(responses or {})
        self.default = default
        self.calls: list[tuple[str, str | None]] = []

    def complete(self, prompt: str, system: str | None = None) -> str:
        self.calls.append((prompt, system))
        if prompt in self.responses:
            return self.responses[prompt]
        if self.default is not None:
            return self.default
        return f"mock:{prompt}"


class AnthropicProvider:
    """Adapter real al SDK Anthropic. Lazy-import: la dep es opcional.

    Requiere `pip install x-dd[anthropic]` + ANTHROPIC_API_KEY.
    Fuera del path de tests (no se ejercita sin red).
    """

    def __init__(self, model: str = "claude-opus-4-8", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY requerido para AnthropicProvider")

    def complete(self, prompt: str, system: str | None = None) -> str:
        try:
            import anthropic  # lazy: dep opcional
        except ImportError as e:  # pragma: no cover - requiere dep externa
            raise ImportError(
                "Instala x-dd[anthropic] para usar AnthropicProvider"
            ) from e
        client = anthropic.Anthropic(api_key=self.api_key)  # pragma: no cover
        msg = client.messages.create(  # pragma: no cover
            model=self.model,
            max_tokens=1024,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text  # pragma: no cover


def _mock_enabled(explicit: bool | None = None) -> bool:
    """Mock activo si --mock, o XDD_PROVIDER_MOCK no es '0'/'false' (default seguro)."""
    if explicit is not None:
        return explicit
    val = os.environ.get("XDD_PROVIDER_MOCK", "1").strip().lower()
    return val not in ("0", "false", "no", "")


def get_provider(
    name: str = "mock",
    *,
    mock: bool | None = None,
    responses: dict[str, str] | None = None,
    default: str | None = None,
    model: str = "claude-opus-4-8",
) -> ProviderPort:
    """Factory de provider. Sin red por defecto (devuelve MockProvider).

    Integra con xdd-router.py: el router decide `name`/`model`; aquí se instancia.
    Real solo si mock desactivado explícitamente Y name no es 'mock'.
    """
    if _mock_enabled(mock) or name == "mock":
        return MockProvider(responses=responses, default=default)
    if name in ("anthropic", "claude"):
        return AnthropicProvider(model=model)
    raise ValueError(f"Provider desconocido: {name!r}")


def _self_test() -> int:
    """Verifica determinismo del MockProvider sin red. Exit 0 si OK."""
    p = get_provider(mock=True, responses={"q": "a"}, default="dflt")
    assert isinstance(p, MockProvider)
    assert isinstance(p, ProviderPort)  # structural check
    assert p.complete("q") == "a"
    assert p.complete("x") == "dflt"
    p2 = get_provider(mock=True)
    assert p2.complete("eco") == "mock:eco"
    assert p2.calls == [("eco", None)]
    # mismas entradas → mismas salidas (determinista)
    assert p.complete("q") == p.complete("q")
    print("[provider] self-test OK — MockProvider determinista, sin red.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="xdd-provider", description=__doc__)
    ap.add_argument("--version", action="version", version=f"xdd-provider {__version__}")
    ap.add_argument("--self-test", action="store_true", help="verifica MockProvider")
    ap.add_argument("--complete", metavar="PROMPT", help="completa un prompt")
    ap.add_argument("--mock", action="store_true", help="fuerza MockProvider")
    ap.add_argument("--name", default="mock", help="provider: mock|anthropic")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()
    if args.complete is not None:
        prov = get_provider(args.name, mock=True if args.mock else None)
        print(prov.complete(args.complete))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
