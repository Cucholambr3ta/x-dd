# 🛡️ Prompt SEC-01: Generar el modelo de amenazas (THREATS.md)

*   **Agente:** `shannon-secops-expert` (de `./prompts/agents/security/shannon-secops-expert.md`)
*   **Workflow:** `/threat-model`
*   **Artefacto Producido:** `docs/specs/THREATS.md`
*   **Palacio de Memoria Loci:** Registrado en la `Room: Auditorías y Seguridad` del proyecto.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agent para inicializar el análisis de amenazas ofensivo:

```markdown
Eres shannon-secops-expert (de la agencia de seguridad) con las habilidades del ecosistema activas.

Proyecto: [PROJ-NombreProyecto]
DOMAIN.md disponible: [pegar contenido completo del DOMAIN.md o su ruta]
SPEC.md borrador disponible: [pegar contenido o ruta]
Stack tecnológico: TypeScript + Node.js + PostgreSQL + Docker + [agregar frameworks como Express o Nest]
Exposición pública: [SÍ/NO — ¿tiene endpoints accesibles directamente desde internet?]
Datos sensibles manejados: [lista: PII de clientes, datos financieros, credenciales, API tokens, etc.]

Tu tarea es generar docs/specs/THREATS.md siguiendo la plantilla 05_secdd_threat_model.md.

PASO 1 — Identificar activos y actores adversarios:
1. Del DOMAIN.md extrae: todos los aggregates, domain events y bounded contexts.
2. Para cada elemento, clasifica los datos que maneja según su criticidad (Confidencial / Restringido / Público).
3. Identifica los actores adversariales y perfiles de ataque más probables para este negocio.
4. Mapea la superficie de ataque física y lógica: endpoints de API, puertos expuestos, bases de datos y pipeline CI/CD.

PASO 2 — Análisis STRIDE por componente:
Para cada aggregate y endpoint expuesto, analiza las 6 categorías de amenazas:
- S (Spoofing - Suplantación): ¿Puede un atacante suplantar identidades de usuarios o servicios?
- T (Tampering - Modificación): ¿Es posible alterar datos en tránsito o en la base de datos?
- R (Repudiation - Repudio): ¿Puede un actor negar haber realizado una transacción sin dejar logs auditables?
- I (Information Disclosure - Revelación): ¿Hay riesgo de fuga de datos en respuestas de error o debug?
- D (Denial of Service - Denegación de servicio): ¿Puede un atacante saturar la memoria o CPU de los endpoints?
- E (Elevation of Privilege - Elevación): ¿Un usuario con rol mínimo puede abusar de las rutas de admin?

Por cada amenaza identificada:
- Asignar un ID: THR-[NNN]
- Describir el vector de ataque específico detalladamente (sin generalidades).
- Estimar Probabilidad (Alta / Media / Baja) e Impacto (Crítico / Alto / Medio / Bajo).
- Calcular el riesgo final.
- Proponer un control técnico de mitigación específico (nombrar la librería exacta o configuración, ej: helmet, rate-limit, Zod schemas).

PASO 3 — Controles y Requisitos de Seguridad:
1. Por cada amenaza calificada como CRÍTICA o ALTA, la implementación del control es BLOCKER antes de salir a producción.
2. Generar el listado de requisitos de seguridad `SEC-REQ-[NNN]` para inyectar en la especificación técnica.
3. Generar la lista de pruebas de seguridad requeridas en la suite `tests/security/`.

Verificación antes de entregar:
- [ ] ¿Cada aggregate del DOMAIN.md tiene al menos una amenaza analizada?
- [ ] ¿Las amenazas críticas tienen controles y tests verificables asociados?

Formato de salida: Markdown estructurado siguiendo la plantilla 05_secdd_threat_model.md.
```
