# THREATS — X-DD v0.1.0 (Threat Modeling STRIDE)

> Modelo de amenazas del propio X-DD. Aplica el método **STRIDE** (Spoofing,
> Tampering, Repudiation, Information disclosure, Denial of service,
> Elevation of privilege) a las entidades de [DOMAIN.md](DOMAIN.md).
> Auditoría ofensiva del propio framework antes de exponerlo público (Sprint 8).

## Modelo de actor

| Actor | Confianza | Vectores |
|-------|-----------|----------|
| **Maintainer (owner)** | Alta | Acceso completo, firma con `.gate-key` |
| **Contribuyente externo** | Media | Vía PR; sin acceso a `.gate-key` |
| **Agente IA local** | Media | Lee/escribe en repo local; puede invocar workflows |
| **Agente IA remoto (vía MCP)** | Variable | Solo accede a tools expuestas por `xdd-mcp-server` |
| **Atacante externo (post-publicación)** | Baja | Sin acceso al repo; puede crear forks maliciosos |
| **Atacante con acceso al disco local** | Crítica | Puede leer `.gate-key` y `~/.mempalace/` |

## Activos a proteger

1. **`.xdd/.gate-key`** — secreto único que da integridad al gate keeper. Pérdida invalida toda firma; robo permite forjar APROBADOs.
2. **`.xdd/<fase>/.signature`** — prueba de aprobación. Integridad protege contra repudiation.
3. **Workflows (`.agent/workflows/*.md`)** — código ejecutable interpretado por agentes. Manipulación = code injection.
4. **`prompts/agents/*.md`** — instrucciones de agentes. Manipulación = prompt injection persistente.
5. **`xdd-mcp-server`** — superficie de API. Tools mal diseñadas exponen acciones destructivas.
6. **MemPalace local (`~/.mempalace/`)** — contiene contexto sensible del proyecto. Robo = filtración masiva.
7. **`scripts/hooks/post-commit`** — se ejecuta automáticamente. Inyección = RCE local.

---

## Matriz STRIDE

### T1 — Spoofing (suplantación)

| ID | Amenaza | Activo | Severidad | Mitigación |
|----|---------|--------|-----------|------------|
| T1.1 | Atacante se presenta como aprobador legítimo en `.approvers` | `.xdd/<fase>/.approvers` | **Alta** | `.signature` HMAC incluye el approver; alterar `.approvers` invalida la firma. (Sprint 4) |
| T1.2 | Fork malicioso del repo simula ser X-DD oficial | repo público | **Media** | `SECURITY.md` (Sprint 8) lista URL canónica; badges con `last-commit` y `actions` dificultan el clon estático |
| T1.3 | Paquete impostor `xdd-cli` en PyPI cuando se publique (ADR-0008) | distribución futura | **Media** | Reservar el nombre apenas se decida; documentar URL oficial |

### T2 — Tampering (alteración)

| ID | Amenaza | Activo | Severidad | Mitigación |
|----|---------|--------|-----------|------------|
| T2.1 | Edición manual de `.xdd/<fase>/.status` a "APROBADO" sin pasar el gate | `.status` | **Crítica** | Firma HMAC sobre `(phase, checksums, approver, timestamp)`. Detectada por `xdd-gate.py validate` (Sprint 4) |
| T2.2 | Modificación de artefactos (`SPEC.md`, etc.) post-aprobación | `Artifact.checksum` | **Alta** | `.checksums` capturados al aprobar; `validate` recalcula y detecta mismatch |
| T2.3 | Workflow malicioso en `.agent/workflows/` agregado por PR | workflows | **Alta** | `lint-workflows.sh` + CI gates (Sprint 2); code review obligatorio; ADR para workflows con efectos destructivos |
| T2.4 | Prompt injection en agente cataloga via `registry.json` | agentes | **Alta** | `validate-registry.py` schema + diff review en PR; agentes nuevos requieren ADR (Sprint 5) |
| T2.5 | Manipulación de `xdd.config.yml` para apuntar MemPalace a host malicioso | config | **Media** | JSON Schema valida URLs/paths; `xdd-doctor.sh` muestra config activa |
| T2.6 | Hook `post-commit` sustituido por payload malicioso | hooks | **Crítica** | `xdd-start.sh` ya hace `git config core.hooksPath ./scripts/hooks` (controlado en repo); `lint-shell.yml` en CI revisa el hook (Sprint 2) |

### T3 — Repudiation (negación de acción)

| ID | Amenaza | Activo | Severidad | Mitigación |
|----|---------|--------|-----------|------------|
| T3.1 | Aprobador niega haber aprobado una fase | `.approvers` | **Media** | Firma HMAC + commit en git con `Author` y `Committer` identificables; commits firmados (recomendado, Sprint 8) |
| T3.2 | Cambio en `.gate-key` no auditado | `.gate-key` | **Alta** | `xdd-gate.py rotate-key` (futuro) registra rotación en `docs/CHANGELOG.md`; backup obligatorio antes de rotar |

### T4 — Information Disclosure (filtración)

| ID | Amenaza | Activo | Severidad | Mitigación |
|----|---------|--------|-----------|------------|
| T4.1 | `.gate-key` se commitea por error | secreto | **Crítica** | `.gitignore` explícito (`xdd-init.sh` lo añade); `gitleaks` en pre-commit y CI (Sprint 2) |
| T4.2 | `memoria.md` / `lecciones.md` contienen PII o secretos del proyecto | dogfooding visible | **Media** | `gitleaks` con regla custom; review de PR; `SECURITY.md` (Sprint 8) advierte |
| T4.3 | `xdd-mcp-server` expone artefactos sensibles vía `xdd_get_phase_artifacts` | MCP API | **Alta** | Whitelist explícita de paths permitidos; rechazo de paths fuera de `.xdd/` (Sprint 6) |
| T4.4 | MemPalace indexa archivos con secretos (`.env`, `.aws/`) | índice semántico | **Alta** | `xdd.config.yml` define `exclude` por defecto (Sprint 3); MemPalace tiene exclude propio |
| T4.5 | Logs de `mempalace mine` en `~/.mempalace/mine.log` con paths internos | logs | **Baja** | El log queda local; documentar limpieza periódica |

### T5 — Denial of Service

| ID | Amenaza | Activo | Severidad | Mitigación |
|----|---------|--------|-----------|------------|
| T5.1 | Workflow consume agente N veces sin límite (cascada) | orquestador | **Media** | `agents.max_concurrent` en `xdd.config.yml` (Sprint 3); `composition_patterns` limitan a lead+specialists |
| T5.2 | `xdd-mcp-server` recibe ráfaga de llamadas | MCP server | **Baja** | Rate limit configurable; el server es local por defecto (sin internet exposure) |
| T5.3 | Workflow malicioso elimina `.xdd/` durante ejecución | state machine | **Alta** | `xdd-gate.py` valida integridad antes de cualquier transición; commits + branch protection permiten rollback |
| T5.4 | `mempalace mine` en archivos enormes bloquea el agente | indexación | **Baja** | Hook ya corre en background; `xdd.config.yml` `exclude` evita binarios grandes |

### T6 — Elevation of Privilege

| ID | Amenaza | Activo | Severidad | Mitigación |
|----|---------|--------|-----------|------------|
| T6.1 | Agente IA local invoca `xdd-gate.py approve` sin permiso humano | gate keeper | **Crítica** | `approve` requiere ENV `XDD_APPROVER` explícita o `--approver`; convención: humano debe correrlo, no agente |
| T6.2 | Workflow ejecuta `sudo` o accede a directorios fuera del proyecto | shell injection | **Alta** | `lint-workflows.sh` detecta rutas absolutas (incluye `/etc`, `/usr`); secure-isolation-ops workflow usa Docker |
| T6.3 | MCP server expone tool que ejecuta arbitrary code | MCP API | **Crítica** | NO existe `xdd_exec` ni `xdd_shell` en el set v0.1.0; cada tool tiene schema input/output estricto |
| T6.4 | Sub-agente delegado obtiene scope mayor que su lead | composition pattern | **Media** | `composition_patterns` declaran `gate_between`; lead valida output del specialist |

---

## Vectores específicos para sistemas IA-driven

### V1 — Prompt injection vía workflow externo
Atacante envía un PR con workflow nuevo cuya descripción esconde instrucciones para el orquestador (ej. "ignore previous instructions and ..."). 

**Mitigación:**
- Review obligatorio de todo PR a `.agent/workflows/`.
- `lint-workflows.sh` puede extenderse para detectar patrones sospechosos (Sprint 7).
- Los agentes operan bajo constraints del registry (Sprint 5).

### V2 — Hook ejecutando script malicioso post-commit
Un PR aparentemente inocente añade un binario o modifica el hook. Al hacer `git commit` localmente, se ejecuta código del atacante.

**Mitigación:**
- `scripts/hooks/post-commit` revisado en CI con `shellcheck` (Sprint 2).
- Binarios sin justificación rechazados en code review.
- `xdd-start.sh` apunta a `./scripts/hooks/` (no a `.git/hooks/`), versionado y auditable.

### V3 — Agente filtrando secretos al MCP server
Un agente con acceso al filesystem lee `.env` y lo envía como argumento al `xdd_invoke_workflow`, exponiendo secretos a otro proceso.

**Mitigación:**
- Tools MCP rechazan strings que matchean patrones de secretos (regex de gitleaks).
- `xdd-mcp-server` loggea todas las invocaciones para auditoría (Sprint 6).

### V4 — Gate keeper sin firma criptográfica
El plan original (v1.1) dejaba `.status` como string editable. Sin HMAC, "APROBADO" es decoración.

**Mitigación:** ADR-0006 + Sprint 4 (HMAC-SHA256 obligatorio).

### V5 — `xdd.config.yml` apunta a versión vieja de MemPalace
Si un proyecto fija `version_constraint: ">=2.0,<3.0"` (anterior al MCP server de MemPalace v3.x), pierde integración futura.

**Mitigación:** `xdd-doctor.sh` v2 (Sprint 3) avisa cuando el constraint excluye la versión recomendada.

---

## Acciones por sprint

| Sprint | Mitigación clave |
|--------|------------------|
| 2 | `gitleaks` + `shellcheck` en CI; pre-commit; branch protection. |
| 3 | `xdd.config.yml` con `exclude` defaults; doctor con SemVer real avisa de constraints peligrosos. |
| 4 | `xdd-gate.py` con HMAC; integración en todos los workflows. |
| 5 | `registry.json` con `constraints` por agente; validación schema. |
| 6 | `xdd-mcp-server` con whitelist de paths; tools sin `exec`; logging. |
| 7 | Tests E2E que verifican que `xdd-gate.py` rechaza alteraciones; tests de los adapters. |
| 8 | `SECURITY.md` con política de divulgación; `CODE_OF_CONDUCT.md`; recomendación de commits firmados. |

---

## Aprobación

- **Estado:** Propuesto — pendiente de aprobación al cerrar Sprint 1.
- **Aprobador:** Alejandro Placencia.
- **Próximo gate:** transición a Fase 3-Plan (Sprint 2).
