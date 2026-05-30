/**
 * commitlint config — X-DD (Sprint 8).
 * Enforced en .github/workflows/lint-commits.yml + pre-commit local.
 *
 * Formato: <type>(<scope>): <subject>
 *
 * Tipos válidos:
 *   feat    — nueva capacidad
 *   fix     — bug fix
 *   docs    — solo documentación
 *   refactor — sin cambio funcional
 *   test    — solo tests
 *   chore   — CI, build, deps, trazabilidad
 *   perf    — mejora de performance
 *   ci      — solo CI
 *   build   — build system
 *   revert  — revert de commit previo
 *
 * Scope sugerido:
 *   - Número de tarea MEJORAS-X-DD.md: feat(1.1), fix(2.2), etc.
 *   - Categoría: docs(adr), chore(trace), feat(sprint-N), test(gate), etc.
 *   - Componente: feat(gate), fix(doctor), feat(mcp), etc.
 */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  // Ignora merge commits (no siguen Conventional Commits por diseño) y reverts auto.
  // Mantiene defaultIgnores de commitlint (fixup!, squash!, etc.).
  ignores: [
    (message) => /^merge:/i.test(message) || /^Merge (branch|pull request|remote-tracking)/i.test(message),
  ],
  defaultIgnores: true,
  rules: {
    // type-enum reemplaza el default
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'refactor', 'test', 'chore', 'perf', 'ci', 'build', 'revert', 'style']
    ],
    // Scope obligatorio (sugerido)
    'scope-empty': [1, 'never'],     // warn si no hay scope (no bloquea)
    // Subject case relajado (acepta español)
    'subject-case': [0],
    // Max longitud del header: 100 (más permisivo que el default 72)
    'header-max-length': [2, 'always', 100],
    // Body line longitud
    'body-max-line-length': [1, 'always', 200],
    // Footer line longitud
    'footer-max-line-length': [1, 'always', 200],
  },
  helpUrl: 'https://github.com/Cucholambr3ta/x-dd/blob/main/CONTRIBUTING.md#reglas-duras',
};
