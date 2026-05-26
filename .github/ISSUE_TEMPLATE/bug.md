---
name: 🐛 Bug report
about: Reportar un bug en X-DD
title: 'bug: '
labels: bug
---

## Descripción

(Una frase clara y concisa de qué falla.)

## Repro

1. ...
2. ...
3. Ver error: ...

## Comportamiento esperado

(Qué debería pasar.)

## Comportamiento actual

(Qué pasa realmente. Incluí stack trace / output del comando.)

## Entorno

```bash
$ bash scripts/xdd-doctor.sh --json | python3 -m json.tool
# pegá la salida acá
```

- OS: (Ubuntu 22.04 / macOS 14 / Windows 11 + WSL2 / etc.)
- Shell: (`bash --version`)
- Python: (`python3 --version`)
- Node: (`node --version`)
- MemPalace: (`mempalace --version` si aplica)

## Contexto adicional

(Logs, screenshots, archivos relevantes.)

## Severidad

- [ ] Crítica (pérdida de datos, security)
- [ ] Alta (funcionalidad core rota)
- [ ] Media (funcionalidad opcional rota, hay workaround)
- [ ] Baja (UX, docs, edge case)
