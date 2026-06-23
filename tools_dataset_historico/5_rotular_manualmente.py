import os
import glob
import tkinter as tk

class Rotulador:
    def __init__(self, root, pasta_cortadas, pasta_destino):
        self.root = root
        self.pasta = pasta_cortadas
        self.pasta_destino = pasta_destino
        
        # Cria a pasta destino se não existir
        if not os.path.exists(self.pasta_destino):
            os.makedirs(self.pasta_destino)
        
        # Pega todos os arquivos na pasta (os já rotulados são movidos para 'renomeada')
        # E ordena por nome para garantir que os grupos fiquem juntos (G00, G01...)
        self.arquivos = glob.glob(os.path.join(self.pasta, "*.png"))
        self.arquivos.sort()
        
        self.index = 0
        
        # Configurar interface visual
        self.lbl_imagem = tk.Label(root)
        self.lbl_imagem.pack(pady=20)
        
        self.lbl_info = tk.Label(root, text="Carregando...", font=("Arial", 14))
        self.lbl_info.pack(pady=10)
        
        self.lbl_instrucao = tk.Label(root, text="Olhe para a letra e aperte a tecla correspondente no teclado.\nO arquivo será MOVIDO para a pasta 'renomeada'.", font=("Arial", 10), fg="gray")
        self.lbl_instrucao.pack(pady=10)
        
        self.root.bind("<Key>", self.tecla_pressionada)
        
        self.mostrar_imagem()
        
    def mostrar_imagem(self):
        if self.index >= len(self.arquivos):
            self.lbl_info.config(text="🎉 Você rotulou todas as imagens! Parabéns!", fg="green")
            self.lbl_imagem.config(image='')
            return
            
        caminho = self.arquivos[self.index]
        
        # Usamos o zoom para aumentar a letra em 5x para você não forçar a vista
        self.photo = tk.PhotoImage(file=caminho).zoom(5, 5)
        self.lbl_imagem.config(image=self.photo)
        
        faltam = len(self.arquivos) - self.index
        self.lbl_info.config(text=f"Faltam: {faltam} imagens.\nAperte a tecla que você está vendo:")
        
    def tecla_pressionada(self, event):
        if self.index >= len(self.arquivos):
            return
            
        char = event.char
        if not char.isalnum():
            return
            
        # Renomear o arquivo
        caminho_antigo = self.arquivos[self.index]
        nome_antigo = os.path.basename(caminho_antigo)
        
        novo_nome = f"{char}_{nome_antigo}"
        # Salva agora na pasta RENOMEADA (movendo o arquivo pra lá)
        caminho_novo = os.path.join(self.pasta_destino, novo_nome)
        
        os.rename(caminho_antigo, caminho_novo)
        
        # Pula para a próxima imagem
        self.index += 1
        self.mostrar_imagem()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Rotulador Turbo 3000")
    root.geometry("500x400")
    
    # Inicia o aplicativo na pasta origem e aponta para a pasta destino
    app = Rotulador(root, "print_captcha_cortado", "renomeada")
    
    root.attributes('-topmost', True)
    root.mainloop()
