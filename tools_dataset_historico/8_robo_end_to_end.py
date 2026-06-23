import os
import glob
import cv2
import numpy as np
import time
import pyautogui
from PIL import ImageGrab
import datetime
import shutil

# ====================================================================
# CONFIGURAÇÕES DA AUTOMAÇÃO
# ====================================================================
COORD_CLIQUE_1 = (430, 450)
COORD_CLIQUE_2 = (443, 496)
BBOX_PRINT = (706, 531, 884, 581)

PASTA_DATABASE = "renomeada"
PASTA_DESTINO = "print_captcha_cortado"

# ====================================================================
# 1. INTELIGÊNCIA DE MEMÓRIA (KNN)
# ====================================================================
def carregar_memoria_knn():
    features = []
    labels = []
    mapa_labels = {} 
    
    # Procura as 35 pastas criadas no passo anterior (A-Z, 1-9)
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
            
            # As imagens no banco estão com fundo branco e letra preta. 
            # Inverter para que a letra fique branca (ajuda na matemática)
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

# ====================================================================
# 2. LIMPEZA E FATIAMENTO CIRÚRGICO
# ====================================================================
def limpar_e_fatiar_imagem(img_cv2):
    # --- LIMPEZA (Versão Aprovada) ---
    img_min = np.min(img_cv2, axis=2)
    mask = cv2.adaptiveThreshold(img_min, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, -15)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    mask_limpa = np.zeros_like(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > 25: # Remove poeiras
            mask_limpa[labels == i] = 255
            
    img_final_limpa = cv2.bitwise_not(mask_limpa) # Fundo branco, letra preta
    
    # --- FATIAMENTO (Connected Components Inteligente) ---
    _, thresh_inv = cv2.threshold(img_final_limpa, 128, 255, cv2.THRESH_BINARY_INV)
    num_labels_cortes, _, stats_cortes, _ = cv2.connectedComponentsWithStats(thresh_inv, connectivity=8)
    
    boxes = []
    for i in range(1, num_labels_cortes):
        x = stats_cortes[i, cv2.CC_STAT_LEFT]
        y = stats_cortes[i, cv2.CC_STAT_TOP]
        w = stats_cortes[i, cv2.CC_STAT_WIDTH]
        h = stats_cortes[i, cv2.CC_STAT_HEIGHT]
        area = stats_cortes[i, cv2.CC_STAT_AREA]
        
        # Filtros de segurança anti-borda
        if area > 15 and w < img_cv2.shape[1] * 0.9 and h < img_cv2.shape[0] * 0.9:
            boxes.append([x, y, w, h])
            
    boxes.sort(key=lambda b: b[0])
    
    # Agrupar letras separadas (como o pingo do i)
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
        
        # Junta se houver sobreposição horizontal > 30%
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
# 3. LOOP AUTÔNOMO DE END-TO-END
# ====================================================================
def main():
    print("1/3 Carregando banco de dados (pasta renomeada)...")
    knn, mapa_labels = carregar_memoria_knn()
    if knn is None:
        print("Erro: Nenhuma imagem organizada na pasta 'renomeada' para consultar.")
        return
        
    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)
        
    print("2/3 Banco de memória carregado com sucesso!")
    print("\nATENÇÃO: O robô assumirá o controle do mouse em 5 segundos.")
    print("Deixe o navegador do Captcha aberto e visível!")
    
    for c in range(5, 0, -1):
        print(f"Iniciando em {c}...")
        time.sleep(1)
    
    relatorio = {}
    total_letras = 0
    
    print("\n3/3 Iniciando Automação...")
    for i in range(500):
        print(f"\n[Ciclo {i+1}/500] Clicando...")
        
        # Sequência de Cliques
        pyautogui.click(COORD_CLIQUE_1[0], COORD_CLIQUE_1[1])
        time.sleep(1.5)
        pyautogui.click(COORD_CLIQUE_2[0], COORD_CLIQUE_2[1])
        time.sleep(1.5)
        
        # Tirar Print e Converter
        print(f"         Tirando foto...")
        img_pil = ImageGrab.grab(bbox=BBOX_PRINT)
        img_cv2 = np.array(img_pil)[:, :, ::-1].copy()
        
        # Limpar e Fatiar
        fatias = limpar_e_fatiar_imagem(img_cv2)
        print(f"         Encontradas {len(fatias)} letras. Classificando...")
        
        # Classificar e Salvar
        for idx_fatia, char_img in enumerate(fatias):
            char_knn = cv2.bitwise_not(char_img) # Deixar letra branca para o KNN
            char_knn = cv2.resize(char_knn, (32, 32))
            feature = char_knn.flatten()
            
            # Buscar imagem mais parecida (k=1)
            ret, results, neighbours, dist = knn.findNearest(np.float32([feature]), k=1)
            classe_predita = mapa_labels[int(ret)]
            
            # Salvar em print_captcha_cortado (Formato: Letra_Data_Hora.png)
            data_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ms = str(datetime.datetime.now().microsecond)[:3]
            nome_arquivo = f"{classe_predita}_{data_hora}_{ms}.png"
            
            caminho_salvar = os.path.join(PASTA_DESTINO, nome_arquivo)
            cv2.imwrite(caminho_salvar, char_img)
            
            # Contabilidade
            relatorio[classe_predita] = relatorio.get(classe_predita, 0) + 1
            total_letras += 1
            
    print("\n==================================")
    print("        RELATÓRIO FINAL           ")
    print("==================================")
    print(f"Total de caracteres lidos com sucesso: {total_letras}")
    for letra, qtd in sorted(relatorio.items()):
        print(f"  -> {qtd} letras '{letra}'")
    print("==================================")
    print(f"As imagens de teste estão na pasta: '{PASTA_DESTINO}'")
    
    print("\n[PAUSA PARA VERIFICAÇÃO HUMANA]")
    print(f"Abra a pasta '{PASTA_DESTINO}' e verifique se as classificações automáticas estão certas.")
    print("Se alguma letra estiver errada, renomeie o arquivo com a letra certa no começo (ex: M_123.png).")
    print("Quando terminar de conferir e arrumar, digite 'ok' aqui e aperte ENTER para arquivar.")
    
    while True:
        resposta = input("> ").strip().lower()
        if resposta == 'ok':
            break
        print("Digite 'ok' quando estiver pronto.")
        
    print("\nArquivando imagens verificadas no banco de dados 'renomeada'...")
    arquivos_pendentes = glob.glob(os.path.join(PASTA_DESTINO, "*.png"))
    
    movidos = 0
    pastas_criadas = set()
    
    for caminho in arquivos_pendentes:
        nome_arquivo = os.path.basename(caminho)
        # O nome começa com a letra certa. Vamos usar a 1ª letra do nome (em maiúsculo).
        letra_classe = nome_arquivo[0].upper()
        
        if not letra_classe.isalnum():
            continue
            
        pasta_classe_destino = os.path.join(PASTA_DATABASE, letra_classe)
        if not os.path.exists(pasta_classe_destino):
            os.makedirs(pasta_classe_destino)
            pastas_criadas.add(letra_classe)
            
        caminho_novo = os.path.join(pasta_classe_destino, nome_arquivo)
        shutil.move(caminho, caminho_novo)
        movidos += 1
        
    print(f"Sucesso Total! {movidos} imagens foram integradas ao banco de dados definitivo e retroalimentaram a IA.")

if __name__ == "__main__":
    main()
