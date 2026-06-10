#!/usr/bin/env bash

# 1. Recupera il percorso dell'immagine corrente da awww query
# Il comando estrae tutto ciò che inizia con "/" (il percorso assoluto del file)
CURRENT_WALL=$(awww query | grep -o '/.*' | head -n 1)

# 2. Se ha trovato un percorso valido, aggiorna il file hyprlock.conf
if [ -n "$CURRENT_WALL" ]; then
    # Cerca la riga che inizia con "path =" e la sostituisce con il nuovo percorso
    sed -i "s|^\s*path = .*|    path = $CURRENT_WALL|" "$HOME/.config/hypr/hyprlock.conf"
fi

# 3. Avvia hyprlock con la configurazione appena aggiornata
hyprlock