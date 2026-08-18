#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  

# --- CONFIGURAZIONE PERCORSI ---
HOME = os.path.expanduser("~")
WALLPAPER_DIR = os.path.join(HOME, "Scaricati")

# Percorsi Wayle
WAYLE_DIR = os.path.join(HOME, ".config/wayle")
WAYLE_CONFIG = os.path.join(WAYLE_DIR, "config.toml")
WAYLE_THEMES_DIR = os.path.join(WAYLE_DIR, "themes")
WAYLE_DEFAULT_THEME = os.path.join(WAYLE_THEMES_DIR, "default.toml")

# Percorsi Wofi e SwayNC (CSS)
WOFI_DIR = os.path.join(HOME, ".config/wofi")
WOFI_LINK = os.path.join(WOFI_DIR, "colore-attuale.css")
SWAYNC_LINK = os.path.join(HOME, ".config/swaync/colore-attuale.css")

# Cartella colori CSS condivisa per SwayNC e Wofi
CSS_THEMES_DIR = os.path.join(HOME, ".config/waybar/colors") 
DEFAULT_CSS_THEME = os.path.join(CSS_THEMES_DIR, "default.css")

VALID_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

class ThemeSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hyprland Theme Selector")
        
        # 1. Calcolo dinamico: Metà della larghezza dello schermo
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = int(screen_width / 2)
        window_height = 450  
        
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        self.root.overrideredirect(True) 
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.configure(bg="#2e3440")
        
        # Scorciatoie globali
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Return>", lambda e: self.apply_theme())

        # Contenitore esterno
        self.outer_box = tk.Frame(root, bg="#2e3440", bd=2, relief="solid", highlightbackground="#4c566a")
        self.outer_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Layout a due colonne
        self.content_layout = tk.Frame(self.outer_box, bg="#2e3440")
        self.content_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- COLONNA SINISTRA (Elenco Temi) ---
        self.left_frame = tk.Frame(self.content_layout, bg="#2e3440")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.listbox = tk.Listbox(
            self.left_frame, 
            font=("JetBrainsMono Nerd Font", 12, "bold"),
            background="#2e3440",
            foreground="#d8dee9",
            selectbackground="#81a1c1", 
            selectforeground="#2e3440", 
            activestyle="none",
            borderwidth=0,
            highlightthickness=0
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # --- COLONNA DESTRA (Anteprima e Azione) ---
        self.right_frame = tk.Frame(self.content_layout, bg="#2e3440")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.preview_container = tk.Frame(self.right_frame, bg="#2e3440")
        self.preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = tk.Label(self.preview_container, bg="#2e3440")
        self.preview_label.pack(expand=True)
        
        self.btn_apply = tk.Button(
            self.right_frame, 
            text="Applica Tema", 
            command=self.apply_theme,
            bg="#4c566a",
            fg="#e5e9f0",
            activebackground="#81a1c1",
            activeforeground="#2e3440",
            relief="flat",
            font=("JetBrainsMono Nerd Font", 12, "bold"),
            pady=8
        )
        self.btn_apply.pack(fill=tk.X, pady=(10, 0))
        
        self.listbox.bind("<<ListboxSelect>>", self.update_preview)
        self.listbox.bind("<Double-1>", lambda event: self.apply_theme())
        
        self.load_wallpapers()
        self.listbox.focus_set()

    def load_wallpapers(self):
        if not os.path.exists(WALLPAPER_DIR):
            messagebox.showerror("Errore", f"La cartella {WALLPAPER_DIR} non esiste.")
            sys.exit(1)
            
        self.wallpapers = [f for f in os.listdir(WALLPAPER_DIR) if f.lower().endswith(VALID_EXTENSIONS)]
        self.wallpapers.sort()
        
        if not self.wallpapers:
            self.listbox.insert(tk.END, "Nessuno sfondo trovato...")
            self.btn_apply.config(state=tk.DISABLED)
            return

        for wp in self.wallpapers:
            name_without_ext = os.path.splitext(wp)[0]
            has_toml = os.path.exists(os.path.join(WAYLE_THEMES_DIR, f"{name_without_ext}.toml"))
            suffix = "  🎨" if has_toml else ""
            self.listbox.insert(tk.END, f" {wp}{suffix}")
            
        self.listbox.selection_set(0)
        self.update_preview(None)

    def update_preview(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        selected_file = self.wallpapers[selection[0]]
        full_wp_path = os.path.join(WALLPAPER_DIR, selected_file)
        
        try:
            img = Image.open(full_wp_path)
            max_width = int((self.root.winfo_screenwidth() / 4) - 40)
            img.thumbnail((max_width, 280)) 
            
            self.photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.photo, text="")
        except Exception:
            self.preview_label.config(image="", text="Anteprima non disponibile", fg="#bf616a")

    def create_symlink(self, target, link_path):
        """Crea o sostituisce atomicamente un symlink (usato per Wofi e SwayNC)."""
        try:
            if os.path.lexists(link_path): 
                os.remove(link_path)
            os.makedirs(os.path.dirname(link_path), exist_ok=True)
            os.symlink(target, link_path)
        except Exception as e:
            print(f"[ERRORE LINK {link_path}] {e}")
    
    def apply_wayle_palette(self, theme_file_path):
        """Legge il file .toml del tema e inietta esplicitamente la sezione [styling.palette] in config.toml."""
        if not os.path.exists(WAYLE_CONFIG) or not os.path.exists(theme_file_path):
            return

        try:
            # 1. Legge le righe del tema TOML (es. red.toml)
            with open(theme_file_path, "r") as f:
                theme_lines = f.readlines()

            # 2. Filtra solo le assegnazioni di colore pulite (chiave = valore)
            clean_color_lines = []
            for line in theme_lines:
                line_str = line.strip()
                # Ignora commenti, righe vuote o l'eventuale header già presente
                if line_str and not line_str.startswith("#") and not line_str.startswith("["):
                    clean_color_lines.append(line_str)

            # 3. Costruisce il blocco TOML formattato correttamente con l'header [styling.palette]
            palette_block = "[styling.palette]\n" + "\n".join(clean_color_lines)

            # 4. Legge il config.toml principale di Wayle
            with open(WAYLE_CONFIG, "r") as f:
                config_content = f.read()

            # 5. Se [styling.palette] esiste già nel file, lo sostituisce; altrimenti lo aggiunge in fondo
            if "[styling.palette]" in config_content:
                # Regex per sostituire da [styling.palette] fino alla sezione successiva o fine file
                pattern = r"\[styling\.palette\][\s\S]*?(?=\n\[|$)"
                updated_config = re.sub(pattern, palette_block, config_content)
            else:
                updated_config = f"{config_content.strip()}\n\n{palette_block}"

            # 6. Sovrascrive fisicamente ~/.config/wayle/config.toml (scatena l'event watcher di Wayle)
            with open(WAYLE_CONFIG, "w") as f:
                f.write(updated_config)

        except Exception as e:
            print(f"[ERRORE AGGIORNAMENTO PALETTE WAYLE] {e}")

    def update_hyprland_borders(self, theme_name, theme_toml_path, theme_css_path):
        """Modifica decorations.lua e lo ri-esegue direttamente tramite hyprctl eval."""
        active_hex = "889b73"    # Fallback Zenbones
        inactive_hex = "3a3634"  # Fallback inattivo
        decorations_file = os.path.expanduser("~/.config/hypr/modules/decorations.lua")

        # 1. Estrazione del colore primario da TOML o CSS
        if theme_toml_path and os.path.exists(theme_toml_path):
            try:
                with open(theme_toml_path, "r") as f:
                    content = f.read()
                    match = re.search(r'(?:primary|accent|fg|green|blue)\s*=\s*["\']#([0-9a-fA-F]{6})["\']', content)
                    if match:
                        active_hex = match.group(1)
            except Exception as e:
                print(f"[ERRORE TOML] {e}")

        elif theme_css_path and os.path.exists(theme_css_path):
            try:
                with open(theme_css_path, "r") as f:
                    content = f.read()
                    match = re.search(r'@define-color\s+(?:accent|primary|fg|text-main|workspaces)\s+#([0-9a-fA-F]{6})', content)
                    if match:
                        active_hex = match.group(1)
                    else:
                        all_hexes = re.findall(r'#([0-9a-fA-F]{6})', content)
                        for h in all_hexes:
                            if h.lower() not in ["000000", "0a0a0a", "121212"]:
                                active_hex = h
                                break
            except Exception as e:
                print(f"[ERRORE CSS] {e}")

        # Stringhe formattate per decorations.lua
        active_color_str = f"rgba({active_hex}ff)"
        inactive_color_str = f"rgba({inactive_hex}aa)"

        # 2. Scrittura diretta in decorations.lua
        if os.path.exists(decorations_file):
            try:
                with open(decorations_file, "r") as f:
                    lua_lines = f.readlines()

                new_lines = []
                for line in lua_lines:
                    if "active_border" in line and "colors" in line:
                        new_lines.append(f'            active_border   = {{ colors = {{"{active_color_str}"}}}},\n')
                    elif "inactive_border" in line:
                        new_lines.append(f'            inactive_border = "{inactive_color_str}",\n')
                    else:
                        new_lines.append(line)

                with open(decorations_file, "w") as f:
                    f.writelines(new_lines)

            except Exception as e:
                print(f"[ERRORE SCRITTURA LUA] {e}")

        # 3. Forziamo la ri-esecuzione di decorations.lua tramite eval per il parser Lua
        try:
            eval_cmd = f"dofile('{decorations_file}')"
            subprocess.run(["hyprctl", "eval", eval_cmd], check=True)
            subprocess.run(["hyprctl", "reload"], check=True)
            print(f"[BORDINI] Cambiati con successo a #{active_hex}")
        except Exception as e:
            print(f"[ERRORE EVAL HYPRLAND] {e}")


    def apply_theme(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        selected_file = self.wallpapers[selection[0]]
        full_wp_path = os.path.join(WALLPAPER_DIR, selected_file)
        theme_name = os.path.splitext(selected_file)[0]
        
        file_toml = os.path.join(WAYLE_THEMES_DIR, f"{theme_name}.toml")
        file_css = os.path.join(CSS_THEMES_DIR, f"{theme_name}.css")
        
        # 1. Controllo demone awww (wallpaper)
        try:
            subprocess.run(["pgrep", "-x", "awww-daemon"], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            subprocess.run(["awww", "init"])
            time.sleep(0.5)
            
        # 2. Applica sfondo
        subprocess.run([
            "awww", "img", full_wp_path,
            "--transition-type", "random",
            "--transition-angle", "30",
            "--transition-step", "90",
            "--transition-fps", "144"
        ])
        
        # 3. Iniezione diretta della palette TOML dentro ~/.config/wayle/config.toml
        sorgente_toml = file_toml if os.path.exists(file_toml) else (WAYLE_DEFAULT_THEME if os.path.exists(WAYLE_DEFAULT_THEME) else None)
        if sorgente_toml:
            self.apply_wayle_palette(sorgente_toml)

        # 4. Gestione Symlink per WOFI e SWAYNC (CSS)
        sorgente_css = file_css if os.path.exists(file_css) else (DEFAULT_CSS_THEME if os.path.exists(DEFAULT_CSS_THEME) else None)
        if sorgente_css:
            for link in [WOFI_LINK, SWAYNC_LINK]:
                self.create_symlink(sorgente_css, link)

        self.update_hyprland_borders(theme_name, sorgente_toml, sorgente_css)

        # 5. Ricarica SwayNC
        try:
            subprocess.run(["pgrep", "-x", "swaync"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["swaync-client", "-rs"])
        except subprocess.CalledProcessError:
            pass

        # 6. Notifica e Uscita
        subprocess.run(["notify-send", f"Cambiato tema generale in {theme_name}"])
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ThemeSelectorApp(root)
    root.mainloop()
