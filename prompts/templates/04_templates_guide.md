# 📄 Guía de Plantillas de Especificación Inmutables

Esta guía describe el propósito de las **7 plantillas de especificación** ubicadas en la carpeta `templates/` y las reglas estrictas que Hermes Agent y Claude Code deben seguir para rellenarlas sin romper el modelado de datos.

---

## 📋 Criterios Generales de Diseño

Todas las especificaciones generadas en base a estas plantillas deben almacenarse en las **Rooms** asociadas al proyecto en **MemPalace** y deben cumplir con las siguientes directivas:
1.  **Formato Markdown Estricto:** Utilizar títulos descriptivos, bloques de código formateados con su respectivo lenguaje y listados cortos y concisos.
2.  **Uso de Alertas Semánticas:** Incorporar alertas de GitHub (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!WARNING]`) para destacar datos críticos de la arquitectura o la seguridad.
3.  **Sin Placeholders:** No se permiten textos descriptivos genéricos o comentarios del tipo `// TODO: implementar`. Cada especificación debe ser concreta y ejecutable.

---

## 📂 Las 7 Plantillas del Ecosistema X-DD

### 1. `00_fdd_feature_catalog.md` (Catálogo de Features FDD)
*   **Propósito:** Define y cataloga las funcionalidades del negocio desde una perspectiva de valor de usuario en `FEATURES.md`.
*   **Secciones Obligatorias:** Listado priorizado de Features, Matriz de puntuación RICE (Reach, Impact, Confidence, Effort) y dependencias críticas entre módulos.

### 2. `01_ddd_domain_model.md` (Modelo de Dominio DDD)
*   **Propósito:** Modelar conceptualmente el dominio del negocio en `DOMAIN.md` para evitar lógica acoplada en la base de datos o en la interfaz.
*   **Secciones Obligatorias:** Glosario de Ubiquitous Language (Lenguaje Ubicuo), Límites de Contextos Acotados (Bounded Contexts), y definición de Entidades, Objetos de Valor (Value Objects) y Agregados.

### 3. `02_bdd_feature_file.md` (Especificación BDD)
*   **Propósito:** Crear escenarios de comportamiento en lenguaje Gherkin en archivos `.feature`.
*   **Secciones Obligatorias:** Escenarios declarativos escritos en español (o inglés, según el estándar del proyecto) estructurados bajo el patrón `Dado / Cuando / Entonces` (Given / When / Then). Debe cubrir casos de éxito y de error lógicos.

### 4. `03_atdd_acceptance.md` (Pruebas de Aceptación ATDD)
*   **Propósito:** Diseñar stubs y pruebas de aceptación ejecutables basadas en el comportamiento (e.g. con Playwright o Cypress) en `qa_[runId]_acceptance.md`.
*   **Secciones Obligatorias:** Configuración del entorno de pruebas, aserciones esperadas del flujo de usuario completo y stubs para simular respuestas de APIs externas.

### 5. `04_tdd_cycle.md` (Guía del Ciclo TDD)
*   **Propósito:** Guía de desarrollo paso a paso del ciclo Red-Green-Refactor para asegurar la calidad de la lógica interna de los componentes.
*   **Secciones Obligatorias:** Aserciones del test fallando (Red), implementación mínima para pasar el test (Green) y refactorización limpia sin romper la cobertura.

### 6. `05_secdd_threat_model.md` (Modelado de Amenazas SecDD)
*   **Propósito:** Analizar la seguridad de la arquitectura del proyecto bajo el framework STRIDE en `THREATS.md`.
*   **Secciones Obligatorias:** Mapeo de flujos de datos, identificación de amenazas por categoría (Suplantación, Manipulación, Repudio, Revelación de información, Denegación de servicio, Elevación de privilegios) y controles de mitigación propuestos.

### 7. `06_stdd_security_cycle.md` (Hardening y Test de Seguridad STDD)
*   **Propósito:** Implementar y automatizar pruebas ofensivas de seguridad (Security Test-Driven Development) para blindar el código en `qa_[runId]_security.md`.
*   **Secciones Obligatorias:** Casos de inyección de payloads ofensivos, validación de schemas robustos con Zod/Prisma y mitigación de OWASP Top 10.

---

## 🛠️ Cómo Ingestar las Plantillas en MemPalace

Cuando se crea un archivo basado en estas plantillas, el agente debe ejecutar el comando de sincronización de MemPalace para indexar el documento dentro de la **Room** de especificación técnica:

```bash
# Sincroniza la nueva especificación en el palacio
mempalace mine /workspace/docs/specs/
```

Esto garantiza que Hermes Agent o cualquier IA del equipo use las especificaciones técnicas activas como el **único origen de la verdad (Single Source of Truth)** para programar lógica funcional o pruebas de regresión.
