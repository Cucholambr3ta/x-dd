# lecciones.md — Fase Retro (Sprint 33: agentix-port → release-ready)

> Aprendizajes de la fase Retro del pipeline X-DD aplicado a sí mismo.
> Sprint 33: portar conceptos del piloto agentix + llevar X-DD a release v0.1.0.
> Formato: `### [CATEGORÍA] Título — fecha` + Contexto / Problema / Causa raíz / Lección / Aplica a.

---

## Resumen de la fase

El piloto **agentix** (réplica white-label de X-DD construida como SDK Python puro, sin MCP)
sirvió de espejo: reveló (a) conceptos que X-DD no tenía y le servían, (b) que MCP no es
necesario, y (c) bugs reales del propio framework al auditarlo. La fase materializó 11 branches
secuenciales con PR a `develop` (cadena pip B1→B3d + independientes B4–B8), cada una con tests
verdes, AgentShield sin críticos y doctor exit 0.

**Entregables:** MockProvider determinista (xdd-provider), gate ejecutable de flujos (xdd-flow),
pip-installable + comando `xdd` (pipx) + publish PyPI OIDC, adapters en código (aditivo),
deprecación de MCP, reubicación de docs de desarrollo, VERSION única, índice ADR completo,
pipeline de release desbloqueado. ADRs 0043–0047 + actualización 0005/0007/0008.

---

## Lecciones

### [PROCESO] Un piloto/réplica es el mejor auditor del framework madre — 2026-05-30
**Contexto:** agentix se construyó como réplica de X-DD en Python puro, sin MCP, por decisión del owner.
**Problema:** X-DD tenía huecos (no testeaba flujos sin red, no era instalable, MCP como peso muerto) que no eran visibles desde dentro.
**Causa raíz:** El sesgo del constructor: lo que se construyó incrementalmente parece completo. Una reimplementación independiente expone lo accidental vs lo esencial.
**Lección:** Cuando exista una réplica o port del sistema, auditarla NO para corregirla, sino para que delate qué del original es accidental. agentix probó que MCP, clone-install y la ausencia de mock-provider eran accidentes, no esencia.
**Aplica a:** Todo framework con pilotos/réplicas. Decisión MCP materializada en ADR-0044.

### [ARQUITECTURA] Empaquetar ≠ reescribir: entry-points finos sobre scripts existentes — 2026-05-30
**Contexto:** ADR-0008 difirió la consolidación CLI por miedo al costo de reescribir todo a Click/Typer.
**Problema:** El `pip install` se necesitaba, pero reescribir 30+ scripts probados era caro y arriesgado.
**Causa raíz:** Se confundió "ser instalable" con "estar consolidado en un CLI idiomático". Son cosas distintas.
**Lección:** Para empaquetar tooling existente, usar dispatchers finos (runpy/subprocess) bajo `[project.scripts]`. Se obtiene `pip install` + entry-points sin tocar la lógica probada. ADR-0043 supersede 0008 sin pagar su costo temido.
**Aplica a:** Empaquetado de cualquier colección de scripts madura. Ver [ADR-0043], [ADR-0045].

### [PROCESO] Cerrar fases gate es acción del aprobador, no del autor — 2026-05-30
**Contexto:** Las fases build/qa/retro del propio repo X-DD necesitaban APROBADO para que release.yml dejara taggear v0.1.0.
**Problema:** El autor (agente) que hizo el trabajo podía firmar el cierre — auto-aprobación, el bug Agent-Anmax.
**Causa raíz:** Tentación de "completar el release de una" firmando uno mismo las fases que uno construyó.
**Lección:** El cierre de fase firma criptográficamente el estado del release. Debe ejecutarlo un aprobador distinto del autor (gate guard self-approve). El agente prepara los artefactos; el humano firma. Se dejó build/qa/retro listas pero SIN aprobar.
**Aplica a:** Todo cierre de fase del pipeline. Refuerza la lección "gate valida contenido no existencia".

### [DEVOPS] Deprecar antes de borrar protege a usuarios y al release — 2026-05-30
**Contexto:** MCP toca 116 archivos + xdd-mcp-server/ + 2 ADRs + 2 test suites. agentix probó que es innecesario.
**Problema:** Borrarlo de golpe rompe a quien lo configuró y mueve 116 archivos justo en el release.
**Causa raíz:** Impulso de "limpiar ya" lo que se demostró innecesario.
**Lección:** Deprecar en el ciclo actual (avisos + ADR + estado de ADRs viejos) y diferir el borrado físico a la siguiente major. El release sale sin romper; los usuarios tienen un ciclo para migrar. ADR-0044 deprecó; el borrado va a v0.2.0.
**Aplica a:** Retiro de cualquier subsistema con usuarios. Ver [ADR-0044].

### [PROCESO] Sé crítico con el alcance: módulo aditivo > reescritura riesgosa — 2026-05-30
**Contexto:** El plan pedía consolidar adapters reescribiendo xdd-adapt.sh (712 líneas, 29 tests bats) a wrapper sobre un módulo Python.
**Problema:** Esa cirugía arriesgaba romper 29 bats + branding/MCP/symlinks + un fix de heredoc reciente, justo antes del release.
**Causa raíz:** El plan asumió la consolidación máxima sin medir el riesgo de regresión real del código probado.
**Lección:** Cuando el alcance pedido es de alto riesgo cerca de un release, reducirlo: portar el patrón como módulo NUEVO aditivo (cero regresión) y diferir la consolidación. Se preguntó al owner y se eligió aditivo. xdd-adapt.sh quedó intacto, 18/18 bats verdes.
**Aplica a:** Cualquier refactor grande sobre código probado con deadline cercano. Ver [ADR-0046].

### [HERRAMIENTAS] Fuente única de versión + test que enforce la coincidencia — 2026-05-30
**Contexto:** La versión estaba hardcodeada en 13 scripts shell + Makefile + agent.yaml + 20 scripts py.
**Problema:** Cada release garantizaba drift: alguna copia quedaba desactualizada.
**Causa raíz:** No había una fuente canónica; cada script declaraba su propia constante.
**Lección:** Un archivo VERSION canónico + scripts que lo leen con fallback + un test que FALLA si cualquier hardcode diverge. La fuente única no basta sin un guard automatizado que detecte la divergencia. Bump de release = editar VERSION; el test bloquea inconsistencias.
**Aplica a:** Cualquier valor replicado en N archivos (versión, endpoints, claves de config). Ver schema/manifest drift.

### [TESTING] Cargar módulos con dataclass vía importlib exige registro en sys.modules — 2026-05-30
**Contexto:** Tests cargan scripts con guion (`xdd-flow.py`) vía `importlib.util.spec_from_file_location`.
**Problema:** `AttributeError: 'NoneType' object has no attribute '__dict__'` al definir dataclasses con `from __future__ import annotations`.
**Causa raíz:** El dataclass resuelve type hints buscando el módulo en `sys.modules`; si se cargó por ruta sin registrarlo bajo su nombre, no está y la resolución falla.
**Lección:** Al cargar por importlib un módulo con dataclasses + annotations diferidas, hacer `sys.modules[name] = mod` ANTES de `exec_module`. Patrón a replicar en todo test que cargue scripts-con-guion que usen dataclasses.
**Aplica a:** Tests de scripts X-DD cargados por ruta. Ver convención importlib en tests/.

### [PROCESO] Branches encadenadas por dependencia: PR contra la base real, no develop — 2026-05-30
**Contexto:** B2 depende de B1, B3 de B2, etc. (cadena pip). B4–B8 independientes.
**Problema:** Si todas las PR apuntan a develop, el diff de cada una incluiría el de sus predecesoras (ruido + conflictos).
**Causa raíz:** Tratar branches dependientes como si fueran independientes.
**Lección:** PR de una branch dependiente apunta a su BASE real (la branch previa), no a develop. Las independientes sí van a develop. El merge respeta el orden: cadena primero (re-apuntando base a develop tras cada merge), independientes en cualquier orden. Mantiene diffs limpios y revisables.
**Aplica a:** Todo trabajo secuencial con dependencias entre branches.

---

> Lecciones transversales ya registradas en lecciones.md de la raíz (no se duplican aquí):
> checks de contenido frágiles al formato, write_file con printf no interpreta escapes.
