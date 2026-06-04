---
description: Ejecución del cierre formal de una fase de desarrollo y actualización de la Memoria Viva de X-DD.
---
# /cierre-fase

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.

**ID:** FLUJO-CIERRE | **Version:** 1.4 | **Agente:** Architect & QA-Reviewer
**Mision:** Certificar el exito de la fase y asegurar la persistencia del conocimiento (Learning Loop).

## 0. CHECKS BLOQUEANTES

> Leccion retroactiva: cierre ejecutado sin gate ni update de lecciones. Ahora son gates bloqueantes.

Ejecuta ANTES de pasar a Seccion 1:

1. **Gate keeper criptografico:**

   ```bash
   python3 scripts/xdd-gate.py validate --phase=<fase-actual>
   ```

   Si exit code != 0: ABORT cierre. Reporta motivo. NO continuar sin resolver.

2. **Sprint number identificado:** determina el numero de sprint actual (ver memoria.md o plan).

3. **Verificar que exista `acuerdos/lecciones/sprint-NN.md` o preparar su creacion (Seccion 2).**

4. **Verificar que exista `acuerdos/memoria/sprint-NN.md` o preparar su creacion (Seccion 3).**

## 1. DESTILACION DE LOGROS

- Resume los hitos alcanzados en la fase actual.
- Verifica contra el Plan de Implementacion que todo este marcado como `[x]`.

## 2. BUCLE DE APRENDIZAJE (POST-MORTEM)

- Identifica cualquier error, bloqueo o gotcha tecnico ocurrido durante el desarrollo.
- **Registro obligatorio en `acuerdos/lecciones/sprint-NN.md`** (formato canonico):

  ```
  ### [CATEGORIA] Titulo breve — YYYY-MM-DD
  **Contexto:** Que estabamos intentando hacer.
  **Problema:** Que fallo o sorprendio.
  **Causa raiz:** Por que paso.
  **Leccion:** Regla aplicable a futuras decisiones.
  **Aplica a:** Ambito (modulo X, todo el proyecto, stack Y...).
  ```

  Categorias: ARQUITECTURA, SEGURIDAD, DOMINIO, TESTING, DEVOPS, PROCESO, HERRAMIENTAS.

- Si el sprint es nuevo: crear el archivo con `xdd-memory.py sprint-close --sprint=NN`.
- Si el archivo ya existe: append directo con las lecciones del sprint.
- **Backward compat:** tambien appendear a `lecciones.md` root (hasta migracion completa).
- Si la solucion es reutilizable: proponer nueva skill en `skills/<name>/SKILL.md`.

## 3. ACTUALIZACION DE MANIFIESTOS

- **`acuerdos/memoria/sprint-NN.md`** — log del sprint (hitos, bloqueos, proxima sesion):

  ```bash
  python3 scripts/xdd-memory.py sprint-close --sprint=NN --project=.
  # Luego editar acuerdos/memoria/sprint-NN.md con el contenido del sprint
  ```

- **`acuerdos/memoria/MEMORY.md`** — actualizar solo si hay hechos persistentes nuevos
  (decisiones de arquitectura, convenciones, riesgos activos).
- **`acuerdos/lecciones/INDEX.md`** — actualizado automaticamente por `sprint-close`.
- **`memoria.md` root** — mantener por backward compat: appendear resumen del sprint.
- **`CLAUDE.md`** — actualizar "Estado Actual" y "Proximo Hito".

## 4. CERTIFICACION DE CALIDAD

Reporte rapido:

- Drift detectado: Si/No
- Tests pasando: Si/No (ejecutar `python3 -m pytest -q`)
- Shield 0 CRITICAL: Si/No (ejecutar `python3 scripts/xdd-shield.py audit --ci`)

## 5. AUTO-ORGANIZE

```bash
XDD_NO_ORGANIZE=1 bash scripts/xdd-organize.sh apply
```

> Nota: si operando en el repo-fuente X-DD, usar `XDD_NO_ORGANIZE=1` para evitar
> que organize añada `scripts/`, `prompts/`, `skills/` al .gitignore (son codigo
> del framework, no artefactos del proyecto consumidor).

## 6. SELLO DE CIERRE — GATE APPROVE OBLIGATORIO

```bash
python3 scripts/xdd-gate.py approve --phase=<fase>
```

- Genera `.xdd/<fase>/.signature` (firma HMAC-SHA256).
- Marca `.xdd/<fase>/.status` = APROBADO.
- Si gate approve falla: ABORT cierre, NO sello verbal.

Termina con timestamp + estatus final + commit message sugerido al usuario.

---

*Driven by X-DD Learning Loop — ADR-0038 + ADR-0041 + Inc5-sprint-memoria*
