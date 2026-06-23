import os
import glob
import shutil

def main():
    pasta_base = "renomeada"
    
    if not os.path.exists(pasta_base):
        print(f"Pasta '{pasta_base}' não encontrada.")
        return
        
    # Pega apenas os arquivos soltos (.png) que estão direto na raiz da pasta
    arquivos = glob.glob(os.path.join(pasta_base, "*.png"))
    
    if not arquivos:
        print(f"Nenhum arquivo solto encontrado na pasta '{pasta_base}'. Eles já podem estar organizados.")
        return
        
    print(f"Organizando {len(arquivos)} imagens em pastas...")
    movidos = 0
    pastas_criadas = set()
    
    for caminho in arquivos:
        nome_arquivo = os.path.basename(caminho)
        
        # O nosso rotulador sempre salva no formato: "A_captcha_..." ou "A_G01_captcha..."
        # Portanto, o primeiro caractere da string é a resposta (label)
        letra = nome_arquivo[0].upper()
        
        # Validação de segurança: garantir que é letra ou número
        if not letra.isalnum():
            continue
            
        pasta_destino = os.path.join(pasta_base, letra)
        
        # Criar a subpasta se não existir
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)
            pastas_criadas.add(letra)
            
        caminho_novo = os.path.join(pasta_destino, nome_arquivo)
        
        # Mover o arquivo
        shutil.move(caminho, caminho_novo)
        movidos += 1
        
    print(f"Sucesso! {movidos} arquivos foram devidamente separados em pastas.")
    if pastas_criadas:
        print(f"Pastas geradas/atualizadas: {', '.join(sorted(pastas_criadas))}")

if __name__ == "__main__":
    main()
