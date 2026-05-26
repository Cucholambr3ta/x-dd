#!/bin/bash
# post:edit:mempalace-index — re-indexa MemPalace en background tras cada Edit/Write.
# Heredado del retrofit original. No bloquea nunca.
set +e
if command -v mempalace >/dev/null 2>&1; then
  ( mempalace mine "$PWD" >>"$HOME/.mempalace/mine.log" 2>&1 & ) >/dev/null 2>&1
fi
exit 0
