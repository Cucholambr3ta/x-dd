#!/bin/bash
# post:edit:mempalace-index — re-indexa MemPalace en background tras cada Edit/Write.
# No bloquea nunca.
#
# Guarda repo X-DD: el settings.json es GLOBAL, así que este hook corre en cualquier
# repo. Sólo re-indexa si $PWD es un proyecto X-DD (tiene .agent/hooks/ o xdd.profile.yml).
#
# Lock skip-if-running: el palace de MemPalace es único global; dos `mine` concurrentes
# chocan ("palace held by PID …"). Adquirimos un flock no-bloqueante; si otro mine corre,
# OMITIMOS este (no encolamos) para no acumular ni ensuciar el log.
set +e

# 1. Guarda: ¿es repo X-DD?
[ -d "$PWD/.agent/hooks" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

# 2. MemPalace disponible
command -v mempalace >/dev/null 2>&1 || exit 0

LOCK="$HOME/.mempalace/.mine.lock"
LOG="$HOME/.mempalace/mine.log"
mkdir -p "$HOME/.mempalace"

# 3. flock -n: si no obtiene el lock (otro mine corre), sale 0 sin ruido.
if command -v flock >/dev/null 2>&1; then
  (
    flock -n 9 || exit 0
    mempalace mine "$PWD" >>"$LOG" 2>&1
  ) 9>"$LOCK" &
else
  # Sin flock: best-effort (comportamiento legacy).
  ( mempalace mine "$PWD" >>"$LOG" 2>&1 & ) >/dev/null 2>&1
fi
exit 0
