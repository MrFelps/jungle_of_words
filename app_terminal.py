import sys
import os
import threading
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class JungleConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Jungle Console")
        self.root.geometry("850x700")
        self.root.configure(bg='black')
        
        self.console = scrolledtext.ScrolledText(
            self.root, 
            bg='black', 
            fg='#00FF00', 
            font=('Consolas', 11, 'bold'), 
            wrap=tk.WORD,
            insertbackground='white'
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.process = None
        self.render_image()
        
        self.console.insert(tk.END, ">>> Pressione ENTER para começar a aventura... <<<\n")
        self.console.configure(state='disabled')
        
        self.root.bind('<Return>', self.start_adventure)

    def render_image(self):
        image_path = resource_path("intro.png")
        if os.path.exists(image_path):
            img = Image.open(image_path)
            target_width = 750
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(img) 
            self.console.image_create(tk.END, image=self.photo)
            self.console.insert(tk.END, "\n\n")
        else:
            self.console.insert(tk.END, "[AVISO] A imagem 'intro.png' não foi embutida!\n\n")

    def print_text(self, text):
        self.console.configure(state='normal')
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        
        self.console.insert(tk.END, clean_text)
        self.console.see(tk.END)
        self.console.configure(state='disabled')

    def start_adventure(self, event):
        self.root.unbind('<Return>')
        self.print_text("\n[SISTEMA] Iniciando a selva de palavras...\n")
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        if getattr(sys, 'frozen', False):
            # Quando estiver no EXE
            comando = [sys.executable, "--backend"]
        else:
            # Quando estiver rodando como .py pelo Python
            comando = [sys.executable, "-u", resource_path("app_leitor_captcha.py")]
            
        # Forçar o envio instantâneo de texto pelo tubo (pipe)
        my_env = os.environ.copy()
        my_env["PYTHONUNBUFFERED"] = "1"
        
        self.process = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            startupinfo=startupinfo,
            env=my_env
        )
        
        thread = threading.Thread(target=self.read_output, daemon=True)
        thread.start()

    def read_output(self):
        for line in iter(self.process.stdout.readline, ''):
            self.root.after(0, self.print_text, line)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--backend":
        # Hack poderoso: substituir o print original por um que FAZ FLUSH OBRIGATÓRIO
        import builtins
        _original_print = builtins.print
        def _flushed_print(*args, **kwargs):
            kwargs['flush'] = True
            _original_print(*args, **kwargs)
        builtins.print = _flushed_print
        
        import app_leitor_captcha
        app_leitor_captcha.main()
    else:
        root = tk.Tk()
        app = JungleConsole(root)
        
        def on_closing():
            if app.process:
                app.process.terminate()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
