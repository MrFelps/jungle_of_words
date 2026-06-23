import os
import glob
import cv2
import numpy as np

def fatiar_imagem(caminho_img, pasta_destino):
    nome_base = os.path.splitext(os.path.basename(caminho_img))[0]
    
    img = cv2.imread(caminho_img, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0
        
    # Inverter: Letra vira branco (255), fundo vira preto (0)
    _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Acha todos os "pedaços" brancos na imagem
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)
    
    boxes = []
    for i in range(1, num_labels): # Ignora o fundo (0)
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        
        # Filtros de Segurança: 
        # Ignora sujeirinhas (area < 15)
        # Ignora linhas de borda que pegam a tela inteira (w > 90% da imagem)
        if area > 15 and w < img.shape[1] * 0.9 and h < img.shape[0] * 0.9:
            boxes.append([x, y, w, h])
            
    if not boxes:
        return 0
        
    # Ordenar as letras da esquerda para a direita
    boxes.sort(key=lambda b: b[0])
    
    # Agrupar pedaços da mesma letra (ex: o pingo do "i" ou do "j")
    merged_boxes = []
    for box in boxes:
        if not merged_boxes:
            merged_boxes.append(box)
            continue
            
        x1, y1, w1, h1 = merged_boxes[-1]
        x2, y2, w2, h2 = box
        
        # Calcular quanto as caixas se sobrepõem na horizontal
        overlap_start = max(x1, x2)
        overlap_end = min(x1 + w1, x2 + w2)
        overlap_len = max(0, overlap_end - overlap_start)
        
        min_w = min(w1, w2)
        
        # Se sobrepõe em mais de 30% da largura do menor pedaço, é a mesma letra!
        if overlap_len > 0.3 * min_w:
            new_x = min(x1, x2)
            new_y = min(y1, y2)
            new_w = max(x1 + w1, x2 + w2) - new_x
            new_h = max(y1 + h1, y2 + h2) - new_y
            merged_boxes[-1] = [new_x, new_y, new_w, new_h]
        else:
            merged_boxes.append(box)
            
    # Salvar as fatias
    cortes_feitos = 0
    for idx, (x, y, w, h) in enumerate(merged_boxes):
        margem = 3 # Margem de respiro para a letra não tocar nas bordas
        y1 = max(0, y - margem)
        y2 = min(img.shape[0], y + h + margem)
        x1 = max(0, x - margem)
        x2 = min(img.shape[1], x + w + margem)
        
        # Cortar a imagem original limpa (letras pretas no fundo branco)
        char_img = img[y1:y2, x1:x2]
        
        nome_arquivo = f"{nome_base}_letra{idx+1}.png"
        caminho_salvar = os.path.join(pasta_destino, nome_arquivo)
        cv2.imwrite(caminho_salvar, char_img)
        cortes_feitos += 1
        
    return cortes_feitos

def main():
    pasta_origem = "print_captcha_letra"
    pasta_destino = "print_captcha_cortado"
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    else:
        # Limpar cortes antigos para não misturar
        antigos = glob.glob(os.path.join(pasta_destino, "*.*"))
        for arq in antigos:
            os.remove(arq)
        
    arquivos = glob.glob(os.path.join(pasta_origem, "*.*"))
    total_imagens = len(arquivos)
    
    if total_imagens == 0:
        print(f"Nenhuma imagem encontrada na pasta {pasta_origem}.")
        return
        
    print(f"Iniciando o fatiamento cirúrgico de {total_imagens} imagens...")
    
    total_cortes = 0
    for idx, caminho in enumerate(arquivos):
        cortes = fatiar_imagem(caminho, pasta_destino)
        total_cortes += cortes
        
        if (idx + 1) % 50 == 0:
            print(f"Processadas {idx + 1}/{total_imagens} imagens...")
            
    print(f"\nMissão Cumprida! {total_cortes} letras individuais foram recortadas cirurgicamente e salvas em '{pasta_destino}'.")

if __name__ == "__main__":
    main()
