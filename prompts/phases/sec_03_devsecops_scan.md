# 🛡️ Prompt SEC-03: Auditoría y escaneo DevSecOps

*   **Agente:** `shannon-secops-expert` (de `./prompts/agents/security/shannon-secops-expert.md`)
*   **Workflow:** `/security-audit`
*   **Artefacto Producido:** `docs/security/AUDIT_REPORT.md` (Reporte de auditoría de seguridad)
*   **Palacio de Memoria Loci:** Registrado en la `Room: Auditorías y Seguridad` del proyecto.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión de seguridad del agente para ejecutar análisis estáticos y dinámicos automáticos:

```markdown
Eres shannon-secops-expert (de la agencia de seguridad) con las habilidades del ecosistema activas.

Proyecto a auditar: [PROJ-NombreProyecto]
Ubicación del repositorio: [ruta relativa o variable de entorno $PWD]

Ejecuta secuencialmente los siguientes pasos de análisis estático y de dependencias. Reporta detalladamente después de cada fase:

=========================================
🛡️ FASE 1 — ANÁLISIS DE DEPENDENCIAS (SCA):
=========================================
1. Ejecuta una auditoría completa del árbol de dependencias de npm para buscar CVEs activos en bibliotecas externas:
   Comando: npm audit --audit-level=high
2. Identifica bibliotecas obsoletas, vulnerables o sin mantenimiento.
3. Propón parches inmediatos (`npm audit fix`) o alternativas en caso de bibliotecas abandonadas.
4. REPORTA: "🛡️ SCA COMPLETADO: CVEs Críticos/Altos detectados: [N]. Mitigaciones recomendadas: [listar]".

=========================================
🛡️ FASE 2 — ANÁLISIS ESTÁTICO DE CÓDIGO (SAST):
=========================================
1. Ejecuta herramientas de escaneo estático de seguridad para buscar patrones vulnerables en el código TypeScript/JavaScript (SQLi estático, XSS estático, inyección de comandos, secretos hardcodeados en repositorios):
   Comandos sugeridos:
   - npx eslint --ext .ts,.js src/ --rule 'no-eval: error'
   - npx gitleaks detect --source=. --verbose (o comandos de regex equivalentes si gitleaks no está instalado)
2. Analiza configuraciones inseguras de CORS, políticas de cookies y headers de respuesta HTTP.
3. REPORTA: "🛡️ SAST COMPLETADO: Alertas críticas de código inseguro: [N]. Problemas de configuración de CORS/Headers: [listar]".

=========================================
🛡️ FASE 3 — CONFIGURACIÓN DE SECRETOS Y ENVIROMENT:
=========================================
1. Audita el archivo `.env.example` y comprueba que ningún valor confidencial real (contraseñas de base de datos de producción, llaves de API, llaves privadas JWT) esté rastreado en Git.
2. Comprueba que exista un mecanismo seguro de inyección de secrets (como VarLock u otra skill aprobada) para evitar fugas.
3. REPORTA: "🛡️ SECRETOS COMPLETADO: Estado de desinfección de archivos .env verificado. Todos los secretos en Git: 0".

Genera el artefacto `docs/security/AUDIT_REPORT.md` estructurado de la siguiente forma:

```markdown
# Reporte de Auditoría DevSecOps — [PROJ-NombreProyecto]
* **Fecha:** [Timestamp ISO]
* **Estado General:** [🟢 CLEAN / 🔴 VULNERABLE]

## 📦 SCA — Análisis de Dependencias
- Dependencias Analizadas: [N]
- Vulnerabilidades Críticas: [N]
- Vulnerabilidades Altas: [N]
- Plan de Acción: [recomendar fixes específicos]

## 🔍 SAST — Análisis Estático de Código
- Archivos Escaneados: [N]
- Violaciones de Seguridad en Código: [N]
- Trazas críticas de fuga de información (ej. logs con PII): [N]
- Plan de Acción: [detallar archivos y líneas a corregir]

## 🔑 Secretos y Configuración
- Fuga de secretos en Git: [Ninguno detectado / 🚨 DETECTADO en archivo X]
- Robustez del `.env.example`: [✅ Correcto]

## ⚖️ Veredicto de Lanzamiento (Gate Keeper)
**Decisión:** [✅ LIBERADO PARA RELEASE / ❌ RETENIDO POR RIESGO DE SEGURIDAD]
```

Restricciones de Calidad:
- Cero dependencias con vulnerabilidad "Critical" o "High" toleradas en el build de producción.
- Cualquier secreto rastreado en Git bloquea automáticamente el pipeline y requiere reescritura del historial de Git.
```
