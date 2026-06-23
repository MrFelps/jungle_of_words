import os
import glob
import cv2
import numpy as np

def main():
    pasta = "print_captcha_cortado"
    arquivos = glob.glob(os.path.join(pasta, "*.png"))
    
    if not arquivos:
        print("Nenhum arquivo encontrado na pasta.")
        return
        
    print(f"Lendo {len(arquivos)} imagens para descobrir padrões de similaridade...")
    features = []
    
    for caminho in arquivos:
        img = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)
        
        # Inverter para que a letra preta fique branca (255)
        # Isso ajuda a matemática a focar apenas no formato da letra, ignorando o fundo branco (0)
        img = cv2.bitwise_not(img)
        
        # Redimensionar para 32x32. Todas as imagens precisam ter o mesmo tamanho para o K-Means comparar
        img = cv2.resize(img, (32, 32))
        
        # Achatar a imagem (transformar o quadrado 32x32 numa linha única de 1024 números)
        features.append(img.flatten())
        
    data = np.float32(features)
    
    # Vamos criar 40 grupos (temos 35 caracteres permitidos + 5 grupos extras para itálicos/letras quebradas)
    K = 40 
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    
    print(f"A Inteligência Artificial K-Means está agrupando em {K} famílias. Aguarde...")
    ret, labels, centers = cv2.kmeans(data, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Renomear os arquivos para adicionar o prefixo do grupo (ex: G05_captcha...)
    print("Renomeando arquivos...")
    for idx, caminho in enumerate(arquivos):
        grupo = labels[idx][0]
        nome_antigo = os.path.basename(caminho)
        
        # Se ele já foi agrupado antes, tira o "GXX_" antigo para não acumular
        if nome_antigo.startswith("G") and nome_antigo[3] == "_":
            nome_antigo = nome_antigo[4:]
            
        novo_nome = f"G{grupo:02d}_{nome_antigo}"
        caminho_novo = os.path.join(pasta, novo_nome)
        os.rename(caminho, caminho_novo)
        
    print("Agrupamento Mágico concluído! Abra o Rotulador Turbo e aproveite!")

if __name__ == "__main__":
    main()
