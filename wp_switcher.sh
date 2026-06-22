#!/usr/bin/env bash

# --- CONFIGURAZIONE PERCORSI PERSONALI ---
WALLPAPER_DIR="$HOME/Scaricati"
WAYBAR_DIR="$HOME/.config/waybar"
WOFI_DIR="$HOME/.config/wofi"
THEMES_DIR="$WAYBAR_DIR/colors"             # Modificato in /colors
LINK_DESTINAZIONE="$WAYBAR_DIR/colore-attuale.css"
WOFI_LINK="$HOME/.config/wofi/colore-attuale.css"
DEFAULT_THEME="$THEMES_DIR/default.css"     # Fallback se manca il tema specifico
SWAYNC_LINK="$HOME/.config/swaync/colore-attuale.css" # Variabile SwayNC mantenuta
CURRENT_WP=$(awww query | grep -o "/.*") #Trova il wallpaper attuale, con grep invece limitiamo l'output solo al path della foto usata

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

# 3. Pesca uno sfondo a caso da ~/Scaricati e poi controlla se è uguale a quello già in uso ed in caso ne ripesca uno finchè non è diverso

RANDOM_WALLPAPER=$(find "$WALLPAPER_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) | shuf -n 1) 
#inizializziamo la variabile almeno una volta perchè deve essere prima inizializzata per fare il confronto dopo 

while [ "$CURRENT_WP" == "$RANDOM_WALLPAPER" ]; do
	RANDOM_WALLPAPER=$(find "$WALLPAPER_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) | shuf -n 1)

	if [ -z "$RANDOM_WALLPAPER" ]; then
	    echo "Nessuno sfondo trovato in $WALLPAPER_DIR"
	    exit 1
	fi
done

#RANDOM_WALLPAPER=$(find "$WALLPAPER_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) | shuf -n 1)

#if [ -z "$RANDOM_WALLPAPER" ]; then
#    echo "Nessuno sfondo trovato in $WALLPAPER_DIR"
#    exit 1
#fi


# 4. Applica lo sfondo con awww
awww img "$RANDOM_WALLPAPER" \
    --transition-type "random" \
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
    ln -sf "$FILE_TEMA" "$SWAYNC_LINK"
    echo "Tema abbinato applicato: colors/$THEME_NAME.css"
elif [ -f "$DEFAULT_THEME" ]; then
    ln -sf "$DEFAULT_THEME" "$LINK_DESTINAZIONE"
    ln -sf "$DEFAULT_THEME" "$WOFI_LINK"
    ln -sf "$DEFAULT_THEME" "$SWAYNC_LINK"
    echo "Tema specifico non trovato in /colors. Applicato default.css"
else
    echo "Avviso: Nessun tema specifico o di default trovato in $THEMES_DIR."
fi

# 7. Aggiorna Waybar all'istante senza riavviarla
# Diamo un attimo di respiro (0.2 secondi) al file system
sleep 0.2

#Verifichiamo se risponde ai segnali standard
if killall -0 waybar 2> /dev/null; then
    # Se è attiva e risponde, ricarica lo stile in sicurezza
    killall -SIGUSR2 waybar
else
    
	killall -9 waybar 2>/dev/null

	sleep 0.2

	#Avviamo waybar in background ma mandiamo il suo output inutile nel buco nero /dev/null
    waybar > /dev/null 2>&1 &
    echo "Waybar era chiusa o crashata. Fatta risorgere in background."
fi

# Invia il segnale di ricarica dello stile a SwayNC
if pgrep -x "swaync" > /dev/null; then
    swaync-client -rs
fi

#Dopo aver aggiornato il tema generale mandiamo una notifica
notify-send "Cambiato tema generale in $THEME_NAME"
