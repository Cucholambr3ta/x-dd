# 🏛️ Guía del Ecosistema X-DD: Hermes Agent + MemPalace

Esta guía técnica describe la arquitectura e instalación paso a paso de tu entorno de desarrollo local-first, totalmente agnóstico de sistemas operativos y basado en estándares de la industria.

---

## 🏗️ Resumen Arquitectónico (Opción A: Montaje Directo)

El ecosistema separa de forma limpia el cerebro (LLM Local), el motor de ejecución autónoma (Hermes en Docker) y el almacén persistente de conocimiento (MemPalace en el Host).

```text
[ Máquina Física (Host) ]
 ├── 🧠 Ollama (Servicio local en puerto 11434)
 ├── 📂 Memoria física (~/.mempalace/ - SQLite + ChromaDB)
 └── 📂 Workspace local ($PWD)
        │
        ▼ (Montajes de Volumen Bidireccionales)
[ Contenedor Docker (Aislamiento de Hermes) ]
 ├── 🤖 Hermes Agent (Ejecutor autónomo)
 ├── 📁 Workspace montado en `/workspace`
 └── 📁 Base de datos montada en `/root/.mempalace`
```

---

## 🚀 Paso 1: Instalación de Dependencias en el Host

### 1. Inferencia Local (Ollama)
Descarga e instala Ollama de forma nativa en tu máquina anfitriona:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Descarga un modelo optimizado para programación:
```bash
ollama run qwen2.5-coder:14b
```

### 2. Almacén de Memoria (MemPalace)
Instala de forma ultra-rápida MemPalace usando `uv` en tu máquina anfitriona:
```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar MemPalace
uv tool install mempalace
```

---

## 🐳 Paso 2: Ejecución del Entorno Hermes en Docker

Para garantizar que Hermes Agent pueda compilar, testear y escribir código sin alterar o dañar tu máquina física, lo levantamos en un contenedor Docker con montajes directos.

### 1. Crear el Dockerfile Optimizado para Hermes + MemPalace
Crea un `Dockerfile` en el directorio de tus herramientas agénticas para construir una imagen con Python y las dependencias del servidor MCP de MemPalace preinstaladas:

```dockerfile
FROM node:20-bookworm-slim

# Instalar Python, Git, Curl y compiladores esenciales
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar MemPalace dentro del contenedor
RUN pip3 install --no-cache-dir mempalace --break-system-packages

# Instalar Hermes Agent globalmente
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

WORKDIR /workspace
CMD ["hermes"]
```

### 2. Arrancar el Contenedor Aislado
Usa el siguiente comando de Docker para levantar la sesión de desarrollo. Nota cómo mapeamos el workspace actual, la base de datos de memoria física y habilitamos el acceso a Ollama del host:

```bash
docker run -it --rm \
  --name hermes-dev \
  --add-host=host.docker.internal:host-gateway \
  -v $PWD:/workspace \
  -v /home/x-dd/.mempalace:/root/.mempalace \
  hermes-dev-image
```

> [!TIP]
> **Compatibilidad Unix/POSIX:**
> Este comando es 100% compatible con cualquier terminal compatible con POSIX. Asegúrate de reemplazar `$PWD` por la ruta absoluta de la Wing en la que desees trabajar.

---

## ⛓️ Paso 3: Configuración del Protocolo MCP de MemPalace

Dado que el volumen `/root/.mempalace` está directamente montado con tu base de datos del host, configuramos Hermes dentro del contenedor para que ejecute el servidor MCP localmente usando pipes estándar (`stdio`).

Configura el archivo `/root/.hermes/mcp_config.json` dentro del contenedor (o realiza la configuración interactiva inicial con `hermes setup`):

```json
{
  "mcpServers": {
    "mempalace": {
      "command": "python3",
      "args": ["-m", "mempalace.mcp_server"],
      "env": {
        "MEMPALACE_DIR": "/root/.mempalace"
      }
    }
  }
}
```

---

## 🧠 Paso 4: Inicializar y Minar (Bootstrap de la Memoria Loci)

La primera vez que entres a un proyecto desde tu nuevo sistema operativo, ejecuta estos comandos en tu host físico para indexar tu base de conocimiento en MemPalace:

```bash
# 1. Inicializar la Bóveda espacial (Wing) para este proyecto
mempalace init $PWD

# 2. Indexar semánticamente todo el código, workflows y plantillas existentes
mempalace mine $PWD
```

Una vez minado, al iniciar Hermes en tu contenedor Docker con `hermes`, el agente consultará automáticamente a través de MCP la base de datos local y recordará al 100% el estado del proyecto, las especificaciones y todas tus decisiones previas de diseño.
