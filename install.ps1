# X-DD Install (PowerShell) — paridad con install.sh / xdd-init.sh para Windows.
# Sprint 7.4. Soporta perfiles desde manifests/install-profiles.json.
#
# Uso:
#   .\install.ps1 [-Dest <path>] [-Profile <name>] [-Modules <csv>] [-ListProfiles] [-Help]
#
# Requiere: PowerShell 5.1+ (Windows 10+) o PowerShell 7+ (cross-platform).

[CmdletBinding()]
param(
    [string]$Dest = "",
    [string]$Profile = "core",
    [string]$Modules = "",
    [switch]$ListProfiles,
    [switch]$Help,
    [switch]$Version
)

$XddVersion = "0.1.0-dev"
$XddRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Show-Usage {
    @"
xdd install.ps1 — bootstrap X-DD en Windows (paridad con install.sh).

Uso:
  .\install.ps1 [-Dest <path>] [-Profile <name>] [-Modules <csv>] [-ListProfiles]
  .\install.ps1 -Help | -Version

Perfiles soportados (manifests/install-profiles.json):
  minimal     Mínimo viable (core + workflows + memory)
  core        Recomendado para empezar (default)
  developer   Completo dev (core + hooks + MCP)
  security    SecDD énfasis
  research    Investigación
  full        Todo

Parámetros:
  -Dest <path>      Ruta destino (default: PWD).
  -Profile <name>   Perfil de install (default: core).
  -Modules <csv>    Override: módulos coma-separados.
  -ListProfiles     Lista perfiles disponibles y sale.
  -Help             Esta ayuda.
  -Version          Versión.

Requiere Python 3.9+ en PATH para resolver manifests.
"@ | Write-Output
}

function Test-Python {
    try {
        $null = & python3 --version 2>&1
        return $true
    } catch {
        try {
            $null = & python --version 2>&1
            return $true
        } catch {
            return $false
        }
    }
}

function Get-PythonCmd {
    try { $null = & python3 --version 2>&1; return "python3" } catch {}
    try { $null = & python --version 2>&1; return "python" } catch {}
    return $null
}

function Show-ListProfiles {
    $manifest = Join-Path $XddRoot "manifests/install-profiles.json"
    if (-not (Test-Path $manifest)) {
        Write-Output "Manifest no encontrado: $manifest"
        return
    }
    $py = Get-PythonCmd
    if (-not $py) {
        Write-Output "(python3 requerido para listar perfiles)"
        return
    }
    Write-Output "Perfiles disponibles:"
    & $py -c @"
import json
d = json.load(open(r'$manifest'))
for name, p in d['profiles'].items():
    print(f'  {name:<10} ({len(p[\"modules\"])} módulos) — {p[\"description\"]}')
"@
}

function Copy-IfAbsent {
    param([string]$Src, [string]$Dst)
    if (Test-Path $Dst) {
        Write-Output "[xdd-install] SKIP existente: $Dst"
        return
    }
    if (-not (Test-Path $Src)) {
        Write-Output "[xdd-install] WARN: source no existe: $Src"
        return
    }
    $parent = Split-Path -Parent $Dst
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    if ((Get-Item $Src).PSIsContainer) {
        Copy-Item -Recurse -Force $Src $Dst
    } else {
        Copy-Item -Force $Src $Dst
    }
    Write-Output "[xdd-install] Copiado: $Dst"
}

# === Entrypoints ===

if ($Help) { Show-Usage; exit 0 }
if ($Version) { Write-Output "xdd install.ps1 v$XddVersion"; exit 0 }
if ($ListProfiles) { Show-ListProfiles; exit 0 }

if (-not $Dest) { $Dest = (Get-Location).Path }
if ($XddRoot -eq $Dest) {
    Write-Error "[xdd-install] ERROR: el destino no puede ser el propio repo X-DD."
    exit 1
}

if (-not (Test-Path $Dest)) {
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
}
Set-Location $Dest

Write-Output "[xdd-install] Origen: $XddRoot"
Write-Output "[xdd-install] Destino: $Dest"
Write-Output "[xdd-install] Perfil: $Profile"

# Resolver archivos vía manifests
$py = Get-PythonCmd
$filesList = @()

if ($Modules) {
    Write-Output "[xdd-install] Módulos override: $Modules"
    if (-not $py) {
        Write-Error "[xdd-install] ERROR: python3 requerido para resolver --modules."
        exit 2
    }
    $manifest = Join-Path $XddRoot "manifests/install-modules.json"
    $scriptText = @"
import json, sys
mods = json.load(open(r'$manifest'))['modules']
requested = '$Modules'.split(',')
files = []
for m in requested:
    m = m.strip()
    if m not in mods:
        print(f'ERROR: módulo desconocido: {m}', file=sys.stderr); sys.exit(1)
    files.extend(mods[m]['files'])
print('\n'.join(sorted(set(files))))
"@
    $filesText = & $py -c $scriptText
    if ($LASTEXITCODE -ne 0) { exit 1 }
    $filesList = $filesText -split "`n" | Where-Object { $_ -ne "" }
} elseif ($py) {
    $pmanifest = Join-Path $XddRoot "manifests/install-profiles.json"
    $mmanifest = Join-Path $XddRoot "manifests/install-modules.json"
    $scriptText = @"
import json, sys
profs = json.load(open(r'$pmanifest'))['profiles']
mods = json.load(open(r'$mmanifest'))['modules']
if '$Profile' not in profs:
    print(f'ERROR: perfil desconocido: $Profile', file=sys.stderr); sys.exit(1)
modules = profs['$Profile']['modules']
files = []
for m in modules:
    if m not in mods:
        continue
    files.extend(mods[m]['files'])
print('\n'.join(sorted(set(files))))
"@
    $filesText = & $py -c $scriptText
    if ($LASTEXITCODE -ne 0) { exit 1 }
    $filesList = $filesText -split "`n" | Where-Object { $_ -ne "" }
} else {
    Write-Output "[xdd-install] WARN: python3 no disponible, fallback legacy."
    $filesList = @(".agent", ".claude", "prompts", "scripts", "templates", "CLAUDE.md")
}

Write-Output "[xdd-install] Archivos a instalar:"
$filesList | ForEach-Object { Write-Output "  - $_" }

foreach ($f in $filesList) {
    $src = Join-Path $XddRoot $f
    $dst = Join-Path $Dest $f
    Copy-IfAbsent -Src $src -Dst $dst
}

# Templates de memoria siempre, si no existen
$memTpl = Join-Path $XddRoot "templates/memoria.template.md"
if ((-not (Test-Path "memoria.md")) -and (Test-Path $memTpl)) {
    Copy-Item -Force $memTpl "memoria.md"
    Write-Output "[xdd-install] memoria.md creado desde template."
}
$lecTpl = Join-Path $XddRoot "templates/lecciones.template.md"
if ((-not (Test-Path "lecciones.md")) -and (Test-Path $lecTpl)) {
    Copy-Item -Force $lecTpl "lecciones.md"
    Write-Output "[xdd-install] lecciones.md creado desde template."
}
$profTpl = Join-Path $XddRoot "templates/xdd.profile.template.yml"
if ((-not (Test-Path "xdd.profile.yml")) -and (Test-Path $profTpl)) {
    Copy-Item -Force $profTpl "xdd.profile.yml"
    Write-Output "[xdd-install] xdd.profile.yml creado desde template."
}

# Git init si no es repo
if (-not (Test-Path ".git")) {
    try {
        & git init -q
        Write-Output "[xdd-install] Repositorio git inicializado."
    } catch {
        Write-Output "[xdd-install] WARN: git no disponible."
    }
}

Write-Output ""
Write-Output "[xdd-install] OK Bootstrap completado en: $Dest"
Write-Output "[xdd-install]   Perfil: $Profile"
Write-Output ""
Write-Output "Siguientes pasos:"
Write-Output "  1. cd `"$Dest`""
Write-Output "  2. Edita memoria.md con la identidad del proyecto."
Write-Output "  3. Edita xdd.profile.yml: tipo de producto y stacks."
Write-Output "  4. Verifica (en WSL o Git Bash):   bash ./scripts/xdd-doctor.sh"
Write-Output "  5. Arranca X-DD (en WSL o Git Bash): bash ./scripts/xdd-start.sh"
Write-Output ""
Write-Output "Otros perfiles disponibles: .\install.ps1 -ListProfiles"
