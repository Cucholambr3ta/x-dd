# Lecciones Sprint 27 — 2026-06-04

> Formato: CATEGORIA / Contexto / Problema / Causa raiz / Leccion / Aplica a.

### [HERRAMIENTAS] sed no maneja emojis Unicode multibyte (ZWJ sequences) — usar Python — 2026-06-04
**Contexto:** Purga masiva de emojis en 52 docs/ de X-DD. Intento inicial con sed y cadena de reemplazos.
**Problema:** sed falla con "dirección de expresión regular sin terminar" para emojis ZWJ como ✅ (U+2705 + FE0F), ⚠️ (U+26A0 + FE0F). El caracter de variacion FE0F rompe el parser de sed.
**Causa raiz:** sed procesa bytes, no codepoints Unicode. Emojis con selector de variacion (FE0F) o ZWJ son multibyte; sed interpreta el FE0F como delimitador de regex.
**Leccion:** Para cualquier operacion masiva de texto con Unicode (emojis, caracteres especiales): usar Python con `re.compile(pattern, re.UNICODE)` y `str.replace()`. sed solo para ASCII puro. Script reutilizable: `python3 -c "EMOJI_PATTERN = re.compile(...); f.write_text(EMOJI_PATTERN.sub('', content))"`.
**Aplica a:** Cualquier purga de caracteres Unicode en X-DD y proyectos generados. Documentar en scripts/xdd-doctor.sh como herramienta de verificacion.

### [ARQUITECTURA] Atomicidad != granularidad — son dimensiones ortogonales de calidad documental — 2026-06-04
**Contexto:** Discusion con compañero del usuario sobre nivel de detalle en documentacion generada por X-DD.
**Problema:** X-DD usaba "granularidad" como criterio pero la metrica correcta es "atomicidad": cada documento cubre exactamente 1 unidad semantica indivisible.
**Causa raiz:** Granularidad mide profundidad dentro del documento. Atomicidad mide cohesion del scope del documento. X-DD_Integration_Guide.md viola atomicidad al mezclar 9 disciplinas en 1 doc.
**Leccion:** Criterio correcto para docs: (1) Atomicidad = 1 doc, 1 dominio tecnico, sin mezclar responsabilidades. (2) Granularidad = profundidad dentro de ese dominio. Un doc atomico puede ser poco granular — ambos son defectos distintos. X-DD_Integration_Guide.md debe dividirse en 9 docs, uno por disciplina (SDD.md, FDD.md, DDD.md, etc.).
**Aplica a:** doc-granular workflow, DOC_STANDARD.md, discipline-check. Tambien aplica a workflows: 1 workflow = 1 operacion.

### [PROCESO] Docs del framework vs docs del proyecto — confusión de scope — 2026-06-04
**Contexto:** Audit de docs X-DD buscando FUNCIONALES.md y NO_FUNCIONALES.md.
**Problema:** Buscamos docs de requisitos en X-DD (el framework) pero esos artefactos son generados POR X-DD para los proyectos que lo usan, no son del framework mismo.
**Causa raiz:** X-DD tiene dos niveles: (1) docs del framework (constitucion, GATE, ARQUITECTURA) y (2) artefactos que X-DD genera en proyectos (SPEC.md, DOMAIN.md, THREATS.md, FUNCIONALES.md). Confundir los dos niveles genera busquedas infructuosas.
**Leccion:** Al auditar docs de X-DD: distinguir explicitamente nivel framework (docs/) vs nivel proyecto (acuerdos/proyecto/, .xdd/). DOC_STANDARD.md aplica a AMBOS niveles pero los artefactos son distintos. Checklist de auditoria debe especificar el nivel objetivo.
**Aplica a:** Futuras auditorias de X-DD y evol-dd. Tambien relevante para xdd-discipline-check.py que valida artefactos de proyecto, no del framework.

