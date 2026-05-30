<!--
  readme.template.md — Plantilla de README "vendible" del flujo X-DD.
  Producido por: scripts/xdd-readme.py vía /cierre-fase (gate `docs`).

  CONVENCIÓN DE CAMPOS
    {{AUTO:campo}}   → rellenado minando el repo real (datos verificables, cero invención).
                       Si el dato no existe, el minero OMITE la sección (no imprime placeholder roto).
    <CONFIGURAR:...> → lo escribe un humano (copy/posicionamiento que el repo no puede inferir).

  El gate `docs` (xdd-gate.py) RECHAZA el README si quedan {{AUTO:...}} o <CONFIGURAR> sin resolver.

  Estructura: síntesis de 4 lentes marketing (Growth · SEO · Content · AI-Citation).
  Orden en CAPAS: Hero vende al decisor en 5s; el cuerpo convierte al desarrollador.
-->

<!-- ════════════ i18n SWITCH (multi-idioma) ════════════ -->
<!-- {{AUTO:readme_translations}} autodetecta hermanos README.<lang>.md y emite la fila de banderas. -->
{{AUTO:readme_translations}}

<!-- ════════════════════════════════════════════════════ -->
<!-- CAPA 1 — HERO (decisor técnico, lectura de 5 segundos) -->
<!-- ════════════════════════════════════════════════════ -->

# {{AUTO:project_name}}

> {{AUTO:definition_sentence}}
<!-- Frase auto-contenida estilo "X is a <categoría> that <función>". Citable literal por LLMs. -->
<!-- AUTO arma el patrón; <CONFIGURAR:category_noun> y <CONFIGURAR:core_function> dan los huecos. -->

<p align="center"><em><CONFIGURAR:tagline></em></p>
<!-- ≤12 palabras, beneficio > feature. Sirve de <meta description> SEO. -->

{{AUTO:badges}}
<!-- lenguaje principal · licencia · versión/release · CI status · coverage. Máx 6. -->

**Quick Facts** <!-- gemelo en texto plano de los badges: los LLMs NO leen imágenes -->
{{AUTO:quick_facts}}
<!-- p.ej: "184 agentes · 43 ADRs · 33 scripts · licencia MIT". Hechos atómicos y atribuibles. -->

## Qué es

<CONFIGURAR:pitch>
<!-- 2-3 frases ≤60 palabras. Frase 1 = dolor. Frase 2 = cómo lo resuelve distinto. -->
<!-- Evita "robusto/escalable/moderno" vacíos. -->

<!-- ════════════════════════════════════════════════════ -->
<!-- CAPA 2 — CUERPO (desarrollador, convierte a clonar/usar) -->
<!-- ════════════════════════════════════════════════════ -->

## Demo

<CONFIGURAR:demo>
<!-- GIF / screenshot / asciinema. Si no hay, esta sección se OMITE (no placeholder vacío). -->

## Quick Start

<!-- Conversión core. Va ALTO. Bloques copy-paste, cero prosa entre comandos. -->

```bash
{{AUTO:install_command}}
{{AUTO:run_command}}
```

**Requisitos:** {{AUTO:prerequisites}}
<!-- versiones/deps detectadas en DEPENDENCIES.md / Cargo.toml / package.json / pyproject. -->

## Por qué {{AUTO:project_name}}

<!-- H2 = query literal que el dev teclea. 3 diferenciadores, no inventario. -->
<CONFIGURAR:differentiators>
<!-- 3 bullets: beneficio en negrita + micro-explicación. -->

## Características

{{AUTO:features}}
<!-- minado de FEATURES.md / catálogo de workflows / scripts. Cada bullet: **sustantivo** — outcome. -->

## Uso / Ejemplos

```{{AUTO:primary_lang}}
{{AUTO:usage_snippet}}
```
<CONFIGURAR:walkthrough>
<!-- Un caso real con input y output > tres triviales. -->

## Arquitectura

<details>
<summary>Cómo funciona (diagrama + flujo)</summary>

```mermaid
{{AUTO:architecture_diagram}}
```
<!-- Mermaid INLINE (crawlable + citable) dentro de <details> (no rompe el flujo del que solo quiere usarlo). -->
<!-- Fases/pipeline numeradas y nombradas: {{AUTO:pipeline_phases}}. -->

{{AUTO:docs_index}}
<!-- links a docs/ con anchor text descriptivo (nunca "click aquí"). -->
</details>

## Configuración

{{AUTO:config_table}}
<!-- tabla | clave | default | descripción | desde xdd.config.yml / schemas / .env.example. -->

<!-- ════════════════════════════════════════════════════ -->
<!-- CAPA 3 — GEO + CONFIANZA (citación AI + objeción final)  -->
<!-- ════════════════════════════════════════════════════ -->

## FAQ

<!-- Mayor leverage GEO: cada ### Pregunta? + respuesta 1-2 frases es citable de forma independiente. -->

### ¿Qué es {{AUTO:project_name}}?
{{AUTO:definition_sentence}}

### ¿Qué requiere para funcionar?
{{AUTO:prerequisites}}

### ¿Bajo qué licencia se distribuye?
{{AUTO:project_name}} se distribuye bajo licencia {{AUTO:license}}.

### ¿En qué se diferencia de las alternativas?
<CONFIGURAR:faq_differentiation>

<!--
  JSON-LD FAQPage para motores crawler-fed (Gemini/Perplexity).
  {{AUTO:faq_jsonld}}
-->

## Comparativa

<CONFIGURAR:comparison_table>
<!-- tabla markdown real: este proyecto en la columna 1; una fila por criterio de decisión. -->
<!-- Gana prompts "X vs Y". Si no defines competidores, esta sección se OMITE. -->

## Calidad & Gates X-DD

{{AUTO:gates_status}}
<!-- gates del pipeline superados + coverage + estado CI. Diferenciador único: gates auditables. -->

## Gobernanza

{{AUTO:governance}}
<!-- license · nº ADRs · SECURITY.md · CODE_OF_CONDUCT.md presentes. Señales de autoridad/E-E-A-T. -->

## Estado del proyecto

> A fecha de {{AUTO:date}}, {{AUTO:project_name}} está en estado **{{AUTO:release_status}}**.
<!-- frase de madurez con recencia (Perplexity pondera frescura). -->

{{AUTO:project_stats}}
<!-- LOC por lenguaje · nº comandos/endpoints · último commit · changelog link. -->

## Contribuir

{{AUTO:contributing}}
<!-- link CONTRIBUTING.md + CODE_OF_CONDUCT.md. -->
<CONFIGURAR:contributing_welcome>
<!-- una frase cálida: "issues y PRs bienvenidos". -->

## Licencia

{{AUTO:project_name}} se distribuye bajo licencia {{AUTO:license}}. {{AUTO:copyright_holder}}

---

<p align="center">{{AUTO:built_with_badge}}</p>
<!-- badge "Built with X-DD" → loop viral: cada README generado anuncia el framework. -->

<!--
  TOPICS (configurar en GitHub repo settings, no en el README):
  {{AUTO:suggested_topics}}
  Los Topics son la faceta de descubrimiento más fuerte de GitHub, separada del texto.
-->
