---
description: Workflow X-DD
---

# /project-architecture-gsd
**ID:** FLUJO-058 | **Versión:** 2.2.0 | **Nivel:** Gobernanza
**Módulo Core:** `skill-project-architect`


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. MISIÓN DEL FLUJO
Garantizar la integridad estructural de los proyectos bajo el estándar `PROJ-*`, gestionando el archivo `conductor.json` como única fuente de verdad para el ciclo de vida y asegurando el aislamiento via Git Worktrees.

## 2. DIRECTRICES INQUEBRANTABLES
- **Aislamiento Físico:** El uso de `scripts/isolate-task.sh` es obligatorio para evitar colisiones entre proyectos y tareas.
- **Conductor First:** Ninguna tarea de ejecución se lanza sin estar definida en los `scripts` de `conductor.json`.
- **Estructura Semántica:** Los directorios deben seguir estrictamente el patrón `/proyecto/{idea,docs,api,design,assets,src,tests}`.
- **Inmutabilidad de Rama Main:** Todo desarrollo ocurre en ramas de característica (`feat/*`) o desarrollo (`develop`).

## 3. DOMINIOS DE CONTROL X-DD
- **Orquestación de Entorno**: Configura el directorio de trabajo y las variables de entorno necesarias.
- **Audit Estructural**: Verifica la presencia de archivos obligatorios (`SAD.md`, `PRD.md`, `memoria.md`).

## 4. ARTÍCULO 6: INTEROPERABILIDAD

La arquitectura del proyecto es la base para la ejecución coordinada:

* **Conector `SEC-ISO` (`FLUJO-071`)**: Este flujo solicita a la arquitectura el aislamiento seguro necesario para las tareas críticas, garantizando que el entorno Git Worktree sea inexpugnable.
* **Conector `CD-DOCS` (`FLUJO-007`)**: La estructura definida aquí dicta la organización de la documentación técnica; si el estándar `PROJ-*` cambia, la sincronización de documentos debe adaptarse automáticamente.
* **Conector `OPS-SYNC` (`FLUJO-072`)**: Al añadir nuevas capacidades estructurales al ecosistema, este flujo coordina la actualización de las plantillas de proyecto.

## 5. FLUJO OPERATIVO DETALLADO
1. **Verificación de Entorno**: Orchestrator comprueba la validez del `conductor.json`.
2. **Instanciación de Workspace**: Se crea el Worktree aislado para la tarea actual.
3. **Sincronización de Dependencias**: Ejecución de `setup` scripts definidos en el JSON.
4. **Validación de Salida**: Tras cada fase, se verifica que los artefactos generados estén en la ubicación correcta según el estándar `PROJ-*`.

## 6. OBSERVABILIDAD (NDJSON)
```json
{
  "timestamp": "ISO-8601",
  "event": "workspace_created",
  "data": {
    "project_id": "string",
    "worktree_path": "string",
    "isolation_status": "SECURE"
  }
}
```

---
**Versión:** 2.2.0 | **Fecha:** 2026-03-20
Desarrollado por la X-DD System


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.