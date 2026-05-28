---
title: Instalación e integración X-DD con VS Code
---

# Instalación X-DD con VS Code + Copilot

Guía granular para integrar X-DD en VS Code aprovechando **prompt files** (slash commands en Copilot Chat), **MCP server**, **tasks** y **terminal env**.

> Pre-requisito: leer [memoria.md](../memoria.md) del proyecto y los disclaimers de licencia en [DEPENDENCIES.md](../DEPENDENCIES.md).

---

## TL;DR (4 comandos)

```bash
# 1) Verificar entorno
bash scripts/xdd-doctor.sh

# 2) Instalar wrapper MCP global (Sprint 25 + ADR-0035)
bash scripts/xdd-mcp-install-global.sh

# 3) Configurar VS Code (auto-genera 4 archivos)
bash scripts/xdd-adapt.sh vscode-copilot --dest=/tu/proyecto

# 4) Reiniciar VS Code → /trigger aparece en Copilot Chat + tasks X-DD en paleta
```

`xdd-adapt vscode-copilot` genera:
- `.github/prompts/*.prompt.md` — slash `/<trigger>` en Copilot Chat (copia real)
- `.vscode/mcp.json` — server X-DD via wrapper global (key `servers`, convención VSCode)
- `.vscode/tasks.json` — 4 tasks comunes: doctor, start, list workflows, gate validate
- `.vscode/settings.json` — env vars terminal (ANTHROPIC_API_KEY, OPENAI_API_KEY)

---

## 1) Requisitos sistema

Linux (Debian/Ubuntu):
```bash
sudo apt update
sudo apt install -y git curl build-essential python3 python3-pip nodejs npm
# docker opcional (sandboxes Sprint 21)
```

macOS:
```bash
brew install git python node
```

Verificar:
```bash
bash scripts/xdd-doctor.sh
# Resumen: N OK, M warnings, 0 críticos
```

## 2) MemPalace — memoria semántica (recomendado, MIT)

**Stack real: Python (PyPI), NO npm.**

```bash
# Vía uv (recomendado, rápido)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install mempalace

# Alternativa pip
pip install --user mempalace

mempalace --version
```

X-DD detecta `mempalace` en `xdd-doctor` + `xdd-start` automáticamente. Sin él, X-DD arranca igual (degrada sin indexación semántica).

Ver [ADR-0004](adr/0004-mempalace-dep-externa-no-fork.md).

## 3) GitNexus — code intelligence (recomendado, ⚠️ PolyForm Noncomm)

```bash
npm install -g gitnexus
# o ad-hoc
npx gitnexus
gitnexus --version
```

> ⚠️ **License PolyForm Noncommercial 1.0.0** — uso personal/research/non-profit gratis. Comercial requiere paid (akonlabs.com). Ver [ADR-0033](adr/0033-gitnexus-tier1-companion.md) + [DEPENDENCIES.md](../DEPENDENCIES.md).

```bash
gitnexus analyze .   # indexa el repo (3-5s codebase mediano)
gitnexus status      # estado del index
gitnexus list        # repos indexados globalmente
```

## 4) Wrapper MCP global X-DD (Sprint 25 + ADR-0035)

Una sola instalación sirve a TODOS tus proyectos:

```bash
bash scripts/xdd-mcp-install-global.sh
# → ~/.local/bin/xdd-mcp-server (wrapper con PYTHONPATH baked)

bash scripts/xdd-mcp-install-global.sh --check
# verifica install + PATH
```

Si `~/.local/bin` no está en PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 5) Adapter VS Code (auto-config)

```bash
bash scripts/xdd-adapt.sh vscode-copilot --dest=/tu/proyecto
```

Auto-genera 4 archivos:

### `.github/prompts/*.prompt.md`
54 workflows como **prompt files**. En Copilot Chat escribís `/<trigger>` (default `/xdd`, custom si rebrandeaste) y aparece el orquestador. **Reinicia VS Code** para que Copilot detecte prompt files nuevos.

### `.vscode/mcp.json`
```json
{
  "servers": {
    "xdd": {
      "command": "/home/<user>/.local/bin/xdd-mcp-server",
      "args": []
    }
  }
}
```
Key `servers` (no `mcpServers` — convención VSCode). Wrapper global = sin `cwd` fijo, dinámico al workspace activo.

### `.vscode/tasks.json` (4 tasks)
- `X-DD: doctor` — verifica entorno
- `X-DD: start orchestrator` — arranca MemPalace + GitNexus + orquestador
- `X-DD: list workflows` — lista workflows + lint
- `X-DD: gate validate (current phase)` — status gate keeper

Uso: `Ctrl+Shift+P` → `Tasks: Run Task` → seleccionar X-DD.

### `.vscode/settings.json` env vars terminal
```json
{
  "terminal.integrated.env.linux": {
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  }
}
```
Hereda env vars del shell padre al terminal integrado VS Code.

## 6) Variables de entorno (API keys)

Export en `~/.bashrc` o `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

⚠️ **NO commitear** `.env` con keys. Usa env vars del shell o secret manager (1Password CLI, Bitwarden, etc.).

## 7) Hooks pre-commit

X-DD activa hooks automáticamente al arrancar:
```bash
bash scripts/xdd-start.sh
# → "Git hook post-commit activado"
```

Hooks incluidos: AgentShield audit (Sprint 12), context budget check (Sprint 19), authz pre-tool (Sprint 21), 6-stage middleware OTel (Sprint 18).

Activación selectiva via profile en `xdd.config.yml`:
```yaml
hooks:
  profile: strict   # minimal | standard | strict
```

## 8) Workflow típico VS Code + Copilot

1. **Abrir proyecto** en VS Code
2. **Copilot Chat** (`Ctrl+Alt+I` o panel) → escribir `/xdd` (o tu trigger custom) → arranca orquestador
3. **Tasks** (`Ctrl+Shift+P` → Run Task) → "X-DD: doctor" / "X-DD: start orchestrator"
4. **MCP tools** disponibles automático en Copilot (xdd_invoke_workflow, xdd_list_agents, etc.)

## 9) Troubleshooting

| Síntoma | Causa | Fix |
|---|---|---|
| `/xdd` no aparece Copilot Chat | prompt files no detectados | Reiniciar VS Code (Reload Window) |
| MCP `xdd` no inicia | wrapper no en PATH | `bash scripts/xdd-mcp-install-global.sh --check` |
| `mempalace` no encontrado | PATH o no instalado | `uv tool install mempalace` |
| `gitnexus` no encontrado | npm global no en PATH | `npm config get prefix` + añadir `/bin` a PATH |
| Orquestador no inicia | claude/opencode no instalados | `npm i -g @anthropic-ai/claude-code` o `npm i -g opencode-ai` |
| Tasks X-DD no aparecen | `.vscode/tasks.json` faltante | re-correr `xdd-adapt vscode-copilot` |

## 10) Seguridad

- **GitNexus** PolyForm Noncomm — revisa antes de uso comercial
- **API keys** — nunca en repo, usar env vars o secret manager
- **xdd-ai-review** (Sprint 16) — pre-procesa diff con gitleaks redact antes de enviar al LLM
- **AgentShield** auditea el propio framework (0 crit/high requerido para release)

## 11) Siguientes pasos

- Extensión VS Code propia con webview UI para findings AI review → roadmap v0.2.0
- Auto-instalador completo dependencies → v0.2.0
- Integración Copilot custom commands API (cuando estable) → v0.2.0

---

## Referencias

- [ADR-0033 GitNexus tier-1](adr/0033-gitnexus-tier1-companion.md)
- [ADR-0034 Universal IDE adapter](adr/0034-universal-ide-adapter.md)
- [ADR-0035 Global install architecture](adr/0035-global-install-architecture.md)
- [docs/IDE_SETUP.md](IDE_SETUP.md) — matriz multi-IDE
- [docs/MCP_INTEGRATION.md](MCP_INTEGRATION.md) — 3 MCP servers (xdd + MemPalace + GitNexus)
- [DEPENDENCIES.md](../DEPENDENCIES.md) — disclaimer licenses
