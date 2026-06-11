# GitNexus — opt-in por licencia comercial

> X-DD integra GitNexus como *code intelligence* opcional, pero **no lo ejecuta por
> defecto** desde v0.2. Esta página explica por qué y cómo activarlo.

## Por qué opt-in

GitNexus se distribuye bajo **PolyForm Noncommercial License**. Esa licencia **prohíbe
el uso comercial**. Como X-DD se usa para desarrollar proyectos que pueden ser comerciales,
ejecutar GitNexus automáticamente expondría al usuario a un incumplimiento de licencia.

Decisión (v0.2, [ADR-0049](adr/0049-gitnexus-optin-licencia-comercial.md)): GitNexus pasa a
ser **opt-in explícito**. X-DD nunca lo invoca salvo que el usuario lo active a sabiendas.

## Qué cambia

| Antes (v0.1.x) | Ahora (v0.2+) |
|---|---|
| `post-commit` corría `gitnexus analyze` si el CLI existía | Solo si `XDD_GITNEXUS=1` |
| `xdd-start` corría `gitnexus index` si el CLI existía | Solo si `XDD_GITNEXUS=1` |
| MemPalace + GitNexus por defecto | **MemPalace (MIT) por defecto**, GitNexus opt-in |

`xdd-doctor` reporta el estado (`gitnexus_enabled: true/false` en `--json`).

## Cómo activarlo (solo proyectos NO comerciales)

```bash
# Por sesión:
export XDD_GITNEXUS=1
bash scripts/xdd-start.sh

# O persistente en tu shell rc (~/.bashrc):
echo 'export XDD_GITNEXUS=1' >> ~/.bashrc
```

Con `XDD_GITNEXUS=1`, el `post-commit` re-indexa el grafo (con flock skip-if-running) y
`xdd-start` corre `gitnexus index`. Sin la variable, ambos son no-op silenciosos.

## Alternativa libre (uso comercial)

**MemPalace (MIT)** ya provee continuidad de contexto entre sesiones — es la dependencia
recomendada por defecto y no tiene restricción comercial. Cubre el caso de "recordar el
proyecto"; lo que se pierde sin GitNexus es el **grafo de código** (impacto/navegación por
símbolos), que no es requisito del pipeline X-DD (los gates y workflows no dependen de él).

Si necesitas grafo de código en un proyecto comercial, usa una herramienta con licencia
permisiva (MIT/Apache) en su lugar; X-DD no acopla a GitNexus en runtime.
