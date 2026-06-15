#!/usr/bin/env bash

# --- CONFIGURAZIONE PERCORSI PERSONALI ---
WALLPAPER_DIR="$HOME/Scaricati"
WAYBAR_DIR="$HOME/.config/waybar"
WOFI_DIR="$HOME/.config/wofi"
THEMES_DIR="$WAYBAR_DIR/colors"             # Modificato in /colors
LINK_DESTINAZIONE="$WAYBAR_DIR/colore-attuale.css"
WOFI_LINK="$HOME/.config/wofi/colore-attuale.css"
DEFAULT_THEME="$THEMES_DIR/default.css"     # Fallback se manca il tema specifico


# 1. Controlla se la cartella Scaricati esiste
if [ ! -d "$WALLPAPER_DIR" ]; then
    echo "Errore: La cartella $WALLPAPER_DIR non esiste."
    exit 1
fi

# 2. Inizializza awww se il daemon non è attivo
if ! pgrep -x "awww-daemon" > /dev/null; then
    awww init
    sleep 0.5
fi

# 3. Pesca uno sfondo a caso da ~/Scaricati
RANDOM_WALLPAPER=$(find "$WALLPAPER_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) | shuf -n 1)

if [ -z "$RANDOM_WALLPAPER" ]; then
    echo "Nessuno sfondo trovato in $WALLPAPER_DIR"
    exit 1
fi

# 4. Applica lo sfondo con awww
awww img "$RANDOM_WALLPAPER" \
    --transition-type "wave" \
    --transition-angle 30 \
    --transition-step 90 \
    --transition-fps 144

echo "Sfondo applicato: $(basename "$RANDOM_WALLPAPER")"

# ==========================================
# GESTIONE DEI COLORI CON SYMLINK
# ==========================================

# 5. Estrae il nome del file senza estensione (es. red.jpg -> red)
FILE_NAME=$(basename "$RANDOM_WALLPAPER")
THEME_NAME="${FILE_NAME%.*}"

FILE_TEMA="$THEMES_DIR/$THEME_NAME.css"

# 6. Crea il collegamento simbolico in base alla presenza del file .css
if [ -f "$FILE_TEMA" ]; then
    ln -sf "$FILE_TEMA" "$LINK_DESTINAZIONE"
    ln -sf "$FILE_TEMA" "$WOFI_LINK"
    echo "Tema abbinato applicato: colors/$THEME_NAME.css"
elif [ -f "$DEFAULT_THEME" ]; then
    ln -sf "$DEFAULT_THEME" "$LINK_DESTINAZIONE"
    ln -sf "$DEFAULT_THEME" "$WOFI_LINK"
    echo "Tema specifico non trovato in /colors. Applicato default.css"
else
    echo "Avviso: Nessun tema specifico o di default trovato in $THEMES_DIR."
fi

# 7. Aggiorna Waybar all'istante senza riavviarla
if pgrep -x "waybar" > /dev/null; then
    killall -SIGUSR2 waybar
fi
