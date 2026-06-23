import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def limpar_captcha(caminho):
    # 1. Carregar a imagem
    img_cv2 = cv2.imread(caminho)
    if img_cv2 is None:
        print("Erro ao carregar a imagem.")
        return

    # 2. O Segredo Universal: Mínimo dos canais RGB
    # Transforma fundos super coloridos em PRETO e mantém fundos cinzas e textos brancos.
    img_min = np.min(img_cv2, axis=2)
    
    # 3. Limpeza Adaptativa (O matador de sombras e fundos)
    mask = cv2.adaptiveThreshold(
        img_min, 
        255, 
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 
        31, 
        -15
    )
    
    # 4. O Aspirador de Pó (Filtro por Área)
    # As letras são grandes (centenas de pixels conectados).
    # O ruído é formado por "poeira" (pontinhos de 1 a 10 pixels conectados).
    # Vamos achar todos os grupos de pixels e APAGAR os que forem menores que 30.
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    
    mask_limpa = np.zeros_like(mask)
    for i in range(1, num_labels): # Pula o índice 0 (que é o fundo preto)
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 25: # Se o grupo tiver mais que 25 pixels, é letra e sobrevive
            mask_limpa[labels == i] = 255
    
    # 5. Inverter: Letra Preta no Fundo Branco
    img_final = cv2.bitwise_not(mask_limpa)
    
    # Exibir o Antes e Depois
    # Aumentar o tamanho para ficar fácil de ver na tela
    img_cv2_grande = cv2.resize(img_cv2, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
    img_final_grande = cv2.resize(img_final, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
    
    import os
    cv2.imwrite("0_captcha_original.png", img_cv2_grande)
    cv2.imwrite("1_captcha_limpo.png", img_final_grande)
    
    # Abre no visualizador padrão de fotos do Windows
    os.startfile("0_captcha_original.png")
    os.startfile("1_captcha_limpo.png")
    
    print("Imagens abertas! Feche as janelas das fotos quando terminar de ver.")

if __name__ == "__main__":
    # Abre uma janela para você selecionar a imagem que quer testar
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal
    
    print("Selecione a imagem do captcha na janela que abriu...")
    caminho_imagem = filedialog.askopenfilename(
        title="Selecione a imagem do Captcha", 
        filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")]
    )
    
    if caminho_imagem:
        limpar_captcha(caminho_imagem)
    else:
        print("Nenhuma imagem selecionada.")
