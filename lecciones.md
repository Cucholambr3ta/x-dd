# lecciones.md — Aprendizajes Acumulados

> Lecciones aprendidas del proyecto. Indexado por MemPalace. Consultado por agentes antes de proponer soluciones para evitar repetir errores (Constitución Art. 9).
> Actualizado vía `/cierre-fase` al final de cada fase.

## Formato
Cada lección sigue la estructura:
```
### [CATEGORÍA] Título breve — YYYY-MM-DD
**Contexto:** Qué estábamos intentando hacer.
**Problema:** Qué falló o sorprendió.
**Causa raíz:** Por qué pasó.
**Lección:** Regla aplicable a futuras decisiones.
**Aplica a:** Ámbito (módulo X, todo el proyecto, stack Y…).
```

Categorías sugeridas: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`, `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.

---

## Lecciones

### [HERRAMIENTAS] `sort -V` es el comparador SemVer portable más simple — 2026-05-26
**Contexto:** Sprint 3 reescribe `xdd-doctor.sh` con comparación de versiones real (no solo `command -v`).
**Problema:** Comparar versiones en bash con `[ "$a" -gt "$b" ]` no funciona (strings); usar herramientas externas (vergleicher, sver) añade deps.
**Causa raíz:** Bash no tiene SemVer nativo; cada solución artesanal con `awk`/regex es propensa a errores con sufijos (`-dev`, `-rc1`, `.post1`).
**Lección:** `sort -V` (`--version-sort`) de coreutils está en todo Linux y macOS modernos. La función `semver_ge() { [ "$(printf '%s\n%s\n' "$min" "$ver" | sort -V | head -n1)" = "$min" ]; }` resuelve el 95% de los casos. Acepta `1.2.3`, `1.2`, sufijos pre-release. Sin deps.
**Aplica a:** Cualquier comparación SemVer en scripts shell. Reutilizable.

### [DEVOPS] `--json` desde el día 1 vale más que UI elegante — 2026-05-26
**Contexto:** Decisión de añadir `--json` a `xdd-doctor.sh` (no estaba en plan v1.1).
**Problema:** Salida solo humana ata el script a uso interactivo; integración con CI/dashboards requiere parseo frágil.
**Causa raíz:** Subestimar futuros consumidores de la herramienta.
**Lección:** Cualquier script de diagnóstico/estado debe ofrecer `--json` (o `--format=json`) desde el primer release. El esfuerzo extra es pequeño y abre integraciones que de otra forma requieren reescritura. Patrón: separar render humano vs JSON con flag temprano.
**Aplica a:** `xdd-gate.py` (Sprint 4), futuras tools del MCP server (Sprint 6), métricas (Sprint 10+).

### [DEVOPS] Branch protection con squash merges deshabilitado bloquea el flujo — 2026-05-26
**Contexto:** Tras pushear Sprint 1, `gh pr merge 2 --squash` falló con "Squash merges are not allowed on this repository".
**Problema:** El repo se creó con configuración default que no permite squash merges; bloquea la convención que el user pidió ("commits + PR + --squash").
**Causa raíz:** GitHub repos heredan `allow_squash_merge` según preferencias del owner, no necesariamente del workflow elegido.
**Lección:** Al crear repo nuevo para X-DD, configurar de inmediato vía API: `allow_squash_merge=true`, `allow_merge_commit=true`, `allow_rebase_merge=false`, `delete_branch_on_merge=true`. Documentar en `INSTALL.md` o `CONTRIBUTING.md` (Sprint 8).
**Aplica a:** Todo repo X-DD nuevo. Considerar añadir a `xdd-init.sh` un paso opcional si hay `gh` + remote configurado.

### [PROCESO] CI primero, refactor después — 2026-05-26
**Contexto:** Sprint 2 añade 4 GitHub Actions antes de implementar el gate keeper (Sprint 4) o el MCP server (Sprint 6).
**Problema:** Tentación de "primero hago el feature, después le pongo CI". Resultado típico: features llegan rotas o sin cobertura.
**Causa raíz:** El CI cuesta poco y atrapa regresiones desde el commit 1. Diferirlo invierte la ecuación.
**Lección:** En todo release público nuevo, los 4 linters básicos (shell + markdown + secrets + custom) van en el sprint 2-3 máximo. Antes de cualquier feature compleja. Las features se construyen sobre CI verde, no al revés.
**Aplica a:** Cualquier proyecto OSS / framework. Reutilizable.

### [HERRAMIENTAS] Edit en scripts requiere Read previo en la misma sesión — 2026-05-26
**Contexto:** Auditando los 4 scripts shell para añadirles `--help` y `--version` (Sprint 1).
**Problema:** El primer Edit sobre `xdd-init.sh` y `xdd-doctor.sh` falló con "File has not been read yet" pese a que ya estaban leídos en mensajes anteriores de la conversación.
**Causa raíz:** El tracker de archivos del agente vincula Read↔Edit por sesión/contexto activo; tras compresión o turnos largos puede perder la asociación.
**Lección:** Si un Edit falla con ese error, hacer un Read corto (10 líneas) del archivo target inmediatamente antes del Edit. Coste mínimo, evita el error y mantiene velocidad.
**Aplica a:** Cualquier edición a archivos previamente vistos pero no editados en la sesión activa.

### [DOMINIO] DOMAIN.md y THREATS.md del framework prueban su propia coherencia — 2026-05-26
**Contexto:** Producción de `.xdd/spec/{DOMAIN,THREATS}.md` del propio X-DD aplicado a sí mismo.
**Problema:** Al escribir DOMAIN.md emergieron entidades que el plan no había nombrado explícitamente: `Capability`, `CompositionPattern`, `MCPTool`, `Approval` como entidad separada de `Gate`. THREATS.md hizo visible que el `xdd-mcp-server` (Sprint 6) requiere whitelist explícita de paths — algo que el plan no detallaba.
**Causa raíz:** Documentar el dominio formalmente fuerza completitud que la planificación táctica omite.
**Lección:** Hacer DOMAIN + THREATS de cualquier proyecto antes de Build no es opcional: descubre entidades y mitigaciones que después serían costosas de retrofitear.
**Aplica a:** Cualquier proyecto X-DD en Fase 2-Spec. Confirma valor de Constitución Art. 4.

### [DEVOPS] Makefile como capa de UX uniforme antes de un CLI completo — 2026-05-26
**Contexto:** Decisión de no consolidar scripts en `xdd` CLI Python aún ([ADR-0008](docs/adr/0008-consolidacion-xdd-cli-diferida.md)).
**Problema:** Sin consolidación, 4+ scripts shell ofrecen UX heterogénea — el usuario necesita recordar nombres distintos.
**Causa raíz:** Diferir refactor no implica aceptar mala UX.
**Lección:** Un Makefile con targets bien nombrados (`make doctor|start|init|lint|test`) ofrece la UX uniforme que un CLI daría, sin el coste de reescribir. Ganamos tiempo manteniendo la calidad de uso.
**Aplica a:** Cualquier conjunto de scripts shell antes de consolidación en CLI. Patrón reutilizable.

### [PROCESO] El gate "APROBADO" como string es seguridad de teatro — 2026-05-26
**Contexto:** Diseñando el gate keeper del Sprint 4 según Tarea 2.2 de MEJORAS-X-DD.md v1.1.
**Problema:** El plan original proponía escribir literal `"APROBADO"` en `.xdd/<fase>/.status`. Ese archivo es trivialmente editable; cualquiera (humano o agente) puede aprobar fases sin enforcement real.
**Causa raíz:** Confundir "convención" con "control". Una vez que el gate keeper existe como código, los stakeholders asumen integridad — pero un string plano no la ofrece.
**Lección:** Cualquier "gate" o "approval" en un sistema agéntico requiere mecanismo criptográfico de integridad (HMAC mínimo). Si la decisión vive en un archivo de texto, debe firmarse contra una clave fuera del control del agente.
**Aplica a:** Cualquier mecanismo de aprobación en X-DD, en proyectos generados por X-DD y en general en frameworks de proceso para sistemas IA. Materializado en [ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md).

### [ARQUITECTURA] "MCP preferido" sin server propio es solo discurso — 2026-05-26
**Contexto:** Revisión de la sección 0.1 del plan v1.1 ("MCP es la vía preferida de integración").
**Problema:** El plan declaraba MCP como preferido pero solo consumía el server de MemPalace; no exponía X-DD vía MCP. Sin server propio, cada IDE nuevo necesitaba su adapter dedicado (9 adapters).
**Causa raíz:** Hueco entre intención declarada y mecanismo implementado.
**Lección:** Si un sistema declara un protocolo como preferido, debe ofrecerlo, no solo consumirlo. Auditar siempre la coherencia entre declaraciones de arquitectura y el código que las implementa.
**Aplica a:** Toda decisión de protocolo/estándar en X-DD. Materializado en [ADR-0005](docs/adr/0005-mcp-preferido-y-server-propio.md).

### [PROCESO] Mini-ciclos X-DD por sprint generan más burocracia que valor — 2026-05-26
**Contexto:** Decidiendo cómo aplicar X-DD a la implementación de MEJORAS.
**Problema:** La opción de "cada sprint = ciclo X-DD completo" (8 sprints × 6 fases = 48 SPEC/PLAN/QA) habría producido decenas de artefactos duplicados sin valor incremental.
**Causa raíz:** Confundir "más X-DD" con "mejor X-DD". La Constitución Art. 9 prohíbe agregar fases, pero no exige multiplicarlas innecesariamente.
**Lección:** Para releases de tamaño medio (≤8 sprints), una sola pasada por las 6 fases es coherente y suficiente. El dogfooding gana por calidad de artefactos, no por cantidad.
**Aplica a:** Cualquier planificación con X-DD sobre un release. Materializado en [ADR-0000](docs/adr/0000-mapeo-mejoras-pipeline-xdd.md).

### [DOMINIO] Confusión de ownership cuando una dep externa se presenta como interna — 2026-05-26
**Contexto:** README anterior describía MemPalace como "pieza del ecosistema X-DD".
**Problema:** Lectores asumían que MemPalace era parte de X-DD; expectativa errónea de soporte, ownership y roadmap unificado.
**Causa raíz:** Lenguaje impreciso sobre límites de sistema. Falta de `DEPENDENCIES.md` explícito.
**Lección:** Cualquier dependencia externa relevante debe declararse en `DEPENDENCIES.md` con versión, licencia, repo y rol. La descripción en README debe usar "integra" o "consume", no "incluye".
**Aplica a:** Todas las deps externas de X-DD y proyectos generados. Materializado en [ADR-0004](docs/adr/0004-mempalace-dep-externa-no-fork.md). Acción en Sprint 1.

### [HERRAMIENTAS] El número de scripts dispersos es señal pero no urgencia — 2026-05-26
**Contexto:** Discusión sobre consolidar 6-8 scripts en `xdd` CLI Python único.
**Problema:** Tentación de "limpiar todo de una vez" reescribiendo todo en Click/Typer ahora.
**Causa raíz:** Sesgo de orden — la dispersión es visible, la consolidación es satisfactoria, pero no agrega valor demostrable a usuarios v0.1.0.
**Lección:** Diferir consolidaciones puramente estéticas hasta tener señal de demanda real (issues de usuarios externos). Un `Makefile` es suficiente para uniformar UX sin reescribir.
**Aplica a:** Decisiones de refactor en X-DD. Materializado en [ADR-0008](docs/adr/0008-consolidacion-xdd-cli-diferida.md).
