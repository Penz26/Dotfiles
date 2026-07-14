#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  

# --- CONFIGURAZIONE PERCORSI ---
HOME = os.path.expanduser("~")
WALLPAPER_DIR = os.path.join(HOME, "Scaricati")
WAYBAR_DIR = os.path.join(HOME, ".config/waybar")
WOFI_DIR = os.path.join(HOME, ".config/wofi")
THEMES_DIR = os.path.join(WAYBAR_DIR, "colors")

LINK_DESTINAZIONE = os.path.join(WAYBAR_DIR, "colore-attuale.css")
WOFI_LINK = os.path.join(WOFI_DIR, "colore-attuale.css")
SWAYNC_LINK = os.path.join(HOME, ".config/swaync/colore-attuale.css")
DEFAULT_THEME = os.path.join(THEMES_DIR, "default.css")

VALID_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

class ThemeSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hyprland Theme Selector")
        
        # 1. Calcolo dinamico: Metà della larghezza dello schermo
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = int(screen_width / 2)
        window_height = 450  # Altezza compatta e proporzionata
        
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        # Stile Wofi senza bordi nativi
        self.root.overrideredirect(True) 
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.configure(bg="#2e3440")
        
        # Scorciatoie globali
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Return>", lambda e: self.apply_theme())

        # Contenitore esterno (Equivalente a #outer-box di Wofi)
        self.outer_box = tk.Frame(root, bg="#2e3440", bd=2, relief="solid", highlightbackground="#4c566a")
        self.outer_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Layout a due colonne (Sinistra: Lista | Destra: Preview e Bottone)
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
            selectbackground="#81a1c1", # Colore accento simile a @wofi-accent
            selectforeground="#2e3440", # @text-opposite
            activestyle="none",
            borderwidth=0,
            highlightthickness=0
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # --- COLONNA DESTRA (Anteprima e Azione) ---
        self.right_frame = tk.Frame(self.content_layout, bg="#2e3440")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Box per centrare verticalmente l'anteprima
        self.preview_container = tk.Frame(self.right_frame, bg="#2e3440")
        self.preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = tk.Label(self.preview_container, bg="#2e3440")
        self.preview_label.pack(expand=True)
        
        # Bottone Applica in fondo alla colonna destra
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
            pady=8  # <-- Sostituito padding=8 con pady=8
        )
        self.btn_apply.pack(fill=tk.X, pady=(10, 0))
        
        # Eventi di selezione e mouse
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
            has_css = os.path.exists(os.path.join(THEMES_DIR, f"{name_without_ext}.css"))
            suffix = "  🎨" if has_css else ""
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
            # Calcola lo spazio disponibile per la preview basandosi sulla colonna destra (metà del totale - padding)
            max_width = int((self.root.winfo_screenwidth() / 4) - 40)
            img.thumbnail((max_width, 280)) 
            
            self.photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.photo, text="")
        except Exception:
            self.preview_label.config(image="", text="Anteprima non disponibile", fg="#bf616a")

    def apply_theme(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        selected_file = self.wallpapers[selection[0]]
        full_wp_path = os.path.join(WALLPAPER_DIR, selected_file)
        theme_name = os.path.splitext(selected_file)[0]
        file_tema = os.path.join(THEMES_DIR, f"{theme_name}.css")
        
        # 1. Controllo demone awww
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
        
        # 3. Gestione Symlink
        if os.path.exists(file_tema):
            sorgente_css = file_tema
        elif os.path.exists(DEFAULT_THEME):
            sorgente_css = DEFAULT_THEME
        else:
            sorgente_css = None

        if sorgente_css:
            for link in [LINK_DESTINAZIONE, WOFI_LINK, SWAYNC_LINK]:
                try:
                    if os.path.lexists(link): 
                        os.remove(link)
                    os.makedirs(os.path.dirname(link), exist_ok=True)
                    os.symlink(sorgente_css, link)
                except Exception as e:
                    print(f"[ERRORE LINK] {e}")

        # 4. Ricarica Waybar
        time.sleep(0.2)
        try:
            subprocess.run(["killall", "-0", "waybar"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["killall", "-SIGUSR2", "waybar"])
        except subprocess.CalledProcessError:
            subprocess.run(["killall", "-9", "waybar"], stderr=subprocess.DEVNULL)
            time.sleep(0.2)
            subprocess.Popen(["waybar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
