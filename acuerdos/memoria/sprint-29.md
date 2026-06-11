# Memoria Sprint 29 — 2026-06-04

> MEGASPRINT: Cerrar 5 gaps del relato (paridad sistema de referencia) + herencia Evol-DD.

## Plan aprobado

| Inc | Gap | Que cierra |
|-----|-----|------------|
| INC-2 | idea.md research-prompt (el puntapie) | idea.md genera prompt de links a investigar |
| INC-1 | Setup repo inicial | /xdd setup-repo: gh repo create + local + dev/collab + ADR-0052 |
| INC-3 | Arsenal seguridad por historia | security-inventory.py: nativas + externas auto-discovery + README |
| INC-4 | Eval desempeno pre-gitflow | xdd-eval.py bloquea gitflow si score bajo |
| INC-5 | doc-granular 4-roles paralelo | documentar grupo 4-roles por doc |
| INC-6 | Mirror + herencia Evol-DD + PyPI 0.3.0 | port con namespace evol-, sin Shannon |

## Decisiones del usuario

- Setup repo: gh repo create (nube) + local + remoto, todas las opciones
- Tools seguridad: segun historia/sprint (relevancia por componente), obligatorias en checklist
- Externas: auto-discovery (usa si instalada, skip con instruccion si no)
- README: documenta TODAS las herramientas ANTES de instalar
- Evol-DD pentest: 100% nativo, SIN Shannon. Exploit-verify = tarea manual
- Equipo ya tiene: nuclei, semgrep, gitleaks, trivy. Falta ZAP

## Arsenal nativo (Python stdlib, sin instalar) — NIVEL 1

scan (SAST SQLi/cmd-inj/XSS), shield (audit), crash (root-cause), patch (auto-fix),
validate (findings), STRIDE modeling, fuzz estatico.

## Externas auto-discovery — NIVEL 2

semgrep, gitleaks, trivy, nuclei, OWASP ZAP (+ Shannon opt-in solo X-DD).

## Hitos

- (en progreso)

## Bloqueos

- (ninguno)

## Proxima sesion

- Verificar herencia Evol-DD v0.3.0 en PyPI
