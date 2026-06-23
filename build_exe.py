import os
import subprocess
from PIL import Image

def build():
    print("===========================================")
    print(" FABRICA DE SOFTWARE - JUNGLE OF WORDS")
    print("===========================================")
    
    if not os.path.exists("icone.ico") and os.path.exists("capa.png"):
        print("Gerando icone.ico a partir da capa.png...")
        img = Image.open("capa.png")
        img_icon = img.resize((256, 256))
        img_icon.save("icone.ico", format="ICO", sizes=[(256, 256)])
        
    print("\nIniciando o PyInstaller (Isso pode levar alguns minutos)...")
    
    import sys
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed", # Esconde qualquer terminal padrão do Windows
        "--name", "Jungle_of_Words",
        "--icon", "icone.ico",
        "--add-data", "renomeada;renomeada",
        "--add-data", "intro.png;.",
        "app_terminal.py"
    ]
    
    subprocess.run(cmd)
    
    print("\n===========================================")
    print(" COMPILAÇÃO FINALIZADA COM SUCESSO!")
    print(" O seu software comercial está na pasta: dist/Jungle_of_Words")
    print("===========================================")

if __name__ == "__main__":
    build()
