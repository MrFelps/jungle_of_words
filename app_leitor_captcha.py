import os
import glob
import cv2
import numpy as np
import time
import keyboard
import pyperclip
import winsound
import tkinter as tk
from PIL import ImageGrab
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

print("Iniciando o carregamento do Banco de Memória (KNN)... Aguarde.")

# ====================================================================
# 1. INTELIGÊNCIA DE MEMÓRIA (KNN)
# ====================================================================
PASTA_DATABASE = resource_path("renomeada")

def carregar_memoria_knn():
    features = []
    labels = []
    mapa_labels = {} 
    
    pastas = glob.glob(os.path.join(PASTA_DATABASE, "*"))
    
    idx_classe = 0
    for pasta in pastas:
        if not os.path.isdir(pasta): continue
        letra_classe = os.path.basename(pasta)
        mapa_labels[idx_classe] = letra_classe
        
        arquivos = glob.glob(os.path.join(pasta, "*.png"))
        for arq in arquivos:
            img = cv2.imread(arq, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
            
            img = cv2.bitwise_not(img)
            img = cv2.resize(img, (32, 32))
            
            features.append(img.flatten())
            labels.append(idx_classe)
            
        idx_classe += 1
            
    if not features:
        return None, None
        
    knn = cv2.ml.KNearest_create()
    knn.train(np.float32(features), cv2.ml.ROW_SAMPLE, np.float32(labels))
    return knn, mapa_labels

knn, mapa_labels = carregar_memoria_knn()

if knn is None:
    print(f"ERRO: Não encontrei imagens no banco de dados '{PASTA_DATABASE}'.")
    exit()

print("Banco de Memória carregado com sucesso! O aplicativo está rodando em segundo plano.")
print("Pressione 'Ctrl+Alt+S' em qualquer lugar para recortar um captcha na tela e dar um Ctrl+C mágico.")

# ====================================================================
# 2. LIMPEZA E FATIAMENTO CIRÚRGICO
# ====================================================================
def limpar_e_fatiar_imagem(img_cv2):
    img_min = np.min(img_cv2, axis=2)
    mask = cv2.adaptiveThreshold(img_min, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, -15)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    mask_limpa = np.zeros_like(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > 25:
            mask_limpa[labels == i] = 255
            
    img_final_limpa = cv2.bitwise_not(mask_limpa)
    
    _, thresh_inv = cv2.threshold(img_final_limpa, 128, 255, cv2.THRESH_BINARY_INV)
    num_labels_cortes, _, stats_cortes, _ = cv2.connectedComponentsWithStats(thresh_inv, connectivity=8)
    
    boxes = []
    for i in range(1, num_labels_cortes):
        x = stats_cortes[i, cv2.CC_STAT_LEFT]
        y = stats_cortes[i, cv2.CC_STAT_TOP]
        w = stats_cortes[i, cv2.CC_STAT_WIDTH]
        h = stats_cortes[i, cv2.CC_STAT_HEIGHT]
        area = stats_cortes[i, cv2.CC_STAT_AREA]
        
        if area > 15 and w < img_cv2.shape[1] * 0.9 and h < img_cv2.shape[0] * 0.9:
            boxes.append([x, y, w, h])
            
    boxes.sort(key=lambda b: b[0])
    
    merged_boxes = []
    for box in boxes:
        if not merged_boxes:
            merged_boxes.append(box)
            continue
        
        x1, y1, w1, h1 = merged_boxes[-1]
        x2, y2, w2, h2 = box
        
        overlap_start = max(x1, x2)
        overlap_end = min(x1 + w1, x2 + w2)
        overlap_len = max(0, overlap_end - overlap_start)
        min_w = min(w1, w2)
        
        if overlap_len > 0.3 * min_w:
            new_x = min(x1, x2)
            new_y = min(y1, y2)
            new_w = max(x1 + w1, x2 + w2) - new_x
            new_h = max(y1 + h1, y2 + h2) - new_y
            merged_boxes[-1] = [new_x, new_y, new_w, new_h]
        else:
            merged_boxes.append(box)
            
    fatias = []
    for x, y, w, h in merged_boxes:
        margem = 3
        y1 = max(0, y - margem)
        y2 = min(img_final_limpa.shape[0], y + h + margem)
        x1 = max(0, x - margem)
        x2 = min(img_final_limpa.shape[1], x + w + margem)
        
        char_img = img_final_limpa[y1:y2, x1:x2]
        fatias.append(char_img)
        
    return fatias

# ====================================================================
# 3. INTERFACE GRÁFICA DE RECORTE (SNIPPING TOOL)
# ====================================================================
class SnippingTool:
    def __init__(self):
        self.root = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None
        self.bg_image = None

    def start(self):
        self.bg_image = ImageGrab.grab()
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.mainloop()

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2, fill="white")

    def on_move_press(self, event):
        self.curX = self.canvas.canvasx(event.x)
        self.curY = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event):
        self.root.destroy()
        
        if self.start_x is None or self.curX is None or self.start_y is None or self.curY is None:
            return

        x1 = min(self.start_x, self.curX)
        y1 = min(self.start_y, self.curY)
        x2 = max(self.start_x, self.curX)
        y2 = max(self.start_y, self.curY)
        
        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10: return
        
        cropped_img = self.bg_image.crop((x1, y1, x2, y2))
        open_cv_image = np.array(cropped_img)[:, :, ::-1].copy()
        
        # Iniciar processo de leitura
        fatias = limpar_e_fatiar_imagem(open_cv_image)
        
        texto_lido = ""
        for char_img in fatias:
            char_knn = cv2.bitwise_not(char_img)
            char_knn = cv2.resize(char_knn, (32, 32))
            feature = char_knn.flatten()
            
            ret, results, neighbours, dist = knn.findNearest(np.float32([feature]), k=1)
            classe_predita = mapa_labels[int(ret)]
            texto_lido += str(classe_predita)
            
        if texto_lido:
            pyperclip.copy(texto_lido)
            print(f"Lido com sucesso: {texto_lido} (Copiado!)")
            winsound.Beep(1000, 200) 
        else:
            print("Não consegui ler nada nesta área.")
            winsound.Beep(500, 200)

is_snipping = False

def iniciar_recorte():
    global is_snipping
    is_snipping = True
    snipper = SnippingTool()
    snipper.start()
    is_snipping = False

def main():
    print("Deixe esta janela aberta/minimizada.")
    global trigger_snip, is_snipping
    trigger_snip = False
    is_snipping = False

    def on_hotkey():
        global trigger_snip, is_snipping
        if not is_snipping:
            trigger_snip = True

    keyboard.add_hotkey('ctrl+alt+s', on_hotkey)
    try:
        while True:
            if trigger_snip:
                trigger_snip = False
                iniciar_recorte()
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("Saindo...")

if __name__ == "__main__":
    main()
