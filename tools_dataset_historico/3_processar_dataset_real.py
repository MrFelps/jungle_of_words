import os
import glob
import cv2
import numpy as np

def limpar_imagem_matematica(img_cv2):
    """Aplica a exata matemática aprovada no testar_limpeza"""
    # 1. Mínimo RGB
    img_min = np.min(img_cv2, axis=2)
    
    # 2. Limpeza Adaptativa
    mask = cv2.adaptiveThreshold(
        img_min, 
        255, 
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 
        31, 
        -15
    )
    
    # 3. Aspirador de Pó (Filtro por Área > 25 pixels)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    mask_limpa = np.zeros_like(mask)
    for i in range(1, num_labels): # Pula o fundo
        area = stats[i, cv2.CC_STAT_AREA]
        if area > 25:
            mask_limpa[labels == i] = 255
            
    # 4. Inverter (Letra preta no fundo branco)
    img_final = cv2.bitwise_not(mask_limpa)
    
    return img_final

def main():
    pasta_origem = "print_captcha"
    pasta_destino = "print_captcha_letra"
    
    # Criar pasta destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta '{pasta_destino}' criada com sucesso!")
        
    # Pegar todas as imagens na pasta origem
    extensoes = ["*.png", "*.jpg", "*.jpeg"]
    arquivos = []
    for ext in extensoes:
        arquivos.extend(glob.glob(os.path.join(pasta_origem, ext)))
        
    total = len(arquivos)
    if total == 0:
        print(f"Aviso: Nenhuma imagem encontrada na pasta '{pasta_origem}'.")
        return
        
    print(f"Iniciando o processamento de {total} imagens...")
    
    sucessos = 0
    for idx, caminho in enumerate(arquivos):
        # Ler imagem
        img_cv2 = cv2.imread(caminho)
        if img_cv2 is None:
            print(f"Erro ao ler imagem: {caminho}")
            continue
            
        # Limpar
        img_limpa = limpar_imagem_matematica(img_cv2)
        
        # Salvar
        nome_arquivo = os.path.basename(caminho)
        caminho_destino = os.path.join(pasta_destino, nome_arquivo)
        cv2.imwrite(caminho_destino, img_limpa)
        
        sucessos += 1
        
        # Printar progresso a cada 50 imagens
        if (idx + 1) % 50 == 0:
            print(f"Processadas {idx + 1}/{total} imagens...")
            
    print(f"\nConcluído! {sucessos} imagens limpas salvas na pasta '{pasta_destino}'.")

if __name__ == "__main__":
    main()
