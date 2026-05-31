# Modos de operación — X-DD

X-DD opera en dos modos según la disponibilidad de MemPalace:

## Modo Completo

MemPalace instalado y activo. Provee continuidad automática de contexto entre sesiones —
el agente "recuerda" el proyecto, las lecciones y los patrones detectados.

**Instalación:** `pip install mempalace` (o ver INSTALL.md sección MemPalace).

**Tiempo de instalación estimado:** ~10 minutos.

Lo que aporta MemPalace sobre el Modo Base:
- Indexación semántica del codebase (búsqueda RAG sobre código y docs).
- Continuidad automática entre sesiones sin repetir contexto manual.
- Pattern-extraction de instincts (S11).

## Modo Base

Sin MemPalace. **El pipeline X-DD funciona completamente** — todos los workflows, todos
los agentes, el Gated Pipeline de 6 fases, las lecciones acumuladas (manual) y los gates
HMAC siguen disponibles.

**Tiempo de instalación:** `pip install x-dd && xdd init` en **< 2 minutos**.

Lo que se pierde en Modo Base:
- Continuidad semántica automática entre sesiones (se puede suplir leyendo `memoria.md` y
  `lecciones.md` manualmente al inicio de cada sesión).
- Búsqueda RAG sobre el codebase.
- Pattern-extraction automática de instincts.

## Detección

`xdd-doctor` detecta el modo activo y lo reporta:

```bash
xdd-doctor           # human-readable: [Modo operativo] COMPLETO / BASE
xdd-doctor --json    # machine-readable: "mempalace_mode": "complete" / "base"
```

`xdd-start` también imprime el modo al arrancar.

## GitNexus (opt-in)

GitNexus es **separado del modo** y siempre opt-in (`XDD_GITNEXUS=1`) por licencia
comercial. Ver [gitnexus-optin.md](gitnexus-optin.md) y [ADR-0049](adr/0049-gitnexus-optin-licencia-comercial.md).
