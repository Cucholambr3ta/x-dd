# X-DD — Guía de Instalación

Esta guía cubre todos los programas necesarios para operar el ecosistema X-DD completo en un sistema Linux/macOS/Windows.

---

## Núcleo Obligatorio

### 1. Claude Code (Orquestador de Agentes)
El CLI que ejecuta los workflows y agentes del sistema.

```bash
# macOS / Linux
npm install -g @anthropic-ai/claude-code

# Verificar instalación
claude --version
```
Requiere cuenta en [claude.ai](https://claude.ai) con acceso a Claude Code.

---

### 2. Git
Control de versiones (GitFlow obligatorio por Constitución Art. 7).

```bash
# Ubuntu / Debian / Mint
sudo apt install git

# macOS
brew install git

# Configuración inicial
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

---

### 3. Node.js v20+ y npm
Runtime para tests, linters y herramientas de desarrollo.

```bash
# Via nvm (recomendado)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | sh
nvm install 20
nvm use 20

# Verificar
node --version   # v20.x.x
npm --version
```

---

### 4. Docker y Docker Compose
Requerido para entornos de staging, DAST y servicios auxiliares.

```bash
# Ubuntu / Mint
sudo apt install docker.io docker-compose-plugin

# Agregar usuario al grupo docker (evitar sudo)
sudo usermod -aG docker $USER
newgrp docker

# macOS
brew install --cask docker

# Verificar
docker --version
docker compose version
```

---

## Testing (Pipeline X-DD)

### 5. Vitest — Tests Unitarios (TDD) y Security Tests (STDD)
```bash
# Por proyecto
npm install -D vitest
```

### 6. Playwright — Tests E2E y BDD
```bash
# Por proyecto
npm install -D @playwright/test
npx playwright install

# Para BDD con archivos .feature
npm install -D playwright-bdd
```

### 7. Cucumber (opcional, alternativa BDD pura)
```bash
npm install -D @cucumber/cucumber
```

---

## Seguridad (Pipeline SecDD)

### 8. Semgrep — SAST (Análisis Estático)
```bash
# Python pip
pip install semgrep

# macOS
brew install semgrep

# Verificar
semgrep --version
```

### 9. Gitleaks — Detección de Secretos en Código
```bash
# Linux (binario)
wget https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz
tar -xzf gitleaks_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/

# macOS
brew install gitleaks

# Verificar
gitleaks version
```

### 10. Trivy — SCA (Vulnerabilidades en Dependencias e Imágenes)
```bash
# Ubuntu / Mint
sudo apt install wget apt-transport-https gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install trivy

# macOS
brew install trivy

# Verificar
trivy --version
```

### 11. OWASP ZAP — DAST (Análisis Dinámico en Staging)
Se ejecuta mediante Docker, no requiere instalación directa:
```bash
# Baseline scan (Tier 2 QA)
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://tu-staging-url

# Full scan
docker run -t owasp/zap2docker-stable zap-full-scan.py -t http://tu-staging-url
```

### 12. Nuclei — Templates de Vulnerabilidades Conocidas
```bash
# Via Go
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# macOS
brew install nuclei

# Actualizar templates
nuclei -update-templates

# Verificar
nuclei -version
```

---

## IDE Recomendado

### VS Code + Extensión Claude Code
```bash
# Instalar VS Code
sudo snap install code --classic

# O descargar desde https://code.visualstudio.com

# Extensión Claude Code: buscar "Claude Code" en el Marketplace
```

### Extensiones VS Code recomendadas
- **Claude Code** — Integración nativa con el orquestador
- **ESLint** — Linting JavaScript/TypeScript
- **Prettier** — Formateo de código
- **GitLens** — Visualización avanzada de git
- **Cucumber (Gherkin)** — Soporte para archivos `.feature`

---

## Verificación de Instalación Completa

```bash
echo "=== X-DD System Check ===" && \
node --version && \
git --version && \
docker --version && \
semgrep --version && \
gitleaks version && \
trivy --version && \
echo "✓ Entorno X-DD listo"
```

---

## Configuración del Proyecto

Al iniciar un proyecto nuevo con X-DD:

```bash
# 1. Clonar / inicializar el repositorio
git init mi-proyecto
cd mi-proyecto

# 2. Copiar la estructura X-DD
cp -r /ruta/a/x-dd/prompts ./prompts
cp -r /ruta/a/x-dd/.agent ./.agent
cp /ruta/a/x-dd/CLAUDE.md ./CLAUDE.md

# 3. Crear archivo de memoria del proyecto
echo "# memoria.md\n## Sesión inicial\nProyecto iniciado." > memoria.md

# 4. Instalar dependencias de testing
npm init -y
npm install -D vitest @playwright/test playwright-bdd

# 5. Iniciar Claude Code
claude
```

---

## Comandos X-DD disponibles (Workflows)

| Comando | Fase | Propósito |
|---------|------|-----------|
| `/xdd` | Todas | Orquestador principal — arranca el flujo del día |
| `/fase-requisitos` | Fase 1 | Briefing → REQUIREMENTS.md + FEATURES.md + .feature stubs |
| `/project-architecture-gsd` | Fase 2 | Spec → SPEC.md + DOMAIN.md + THREATS.md |
| `/plan-fases` | Fase 3 | Plan → PLAN.md organizado por features (FDD) |
| `/xdd-build` | Fase 4 | Build con TDD + STDD integrados |
| `/qa-review` | Fase 5 | QA completo: Tier 1 (SAST) + Tier 2 (BDD/ATDD/DAST) + Tier 3 (LLM-Judge) |
| `/cierre-fase` | Fase 6 | Retro → lecciones.md + memoria.md actualizado |
| `/security-audit` | Fase 5 | Auditoría de seguridad completa |
| `/advanced-agentic-pentesting` | Demanda | Red Team ofensivo con SecOps |

---
*X-DD System — Instalación y configuración*
