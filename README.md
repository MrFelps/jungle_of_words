# Jungle of Words 🌴

<div align="center">
  <img src="intro.png" alt="Jungle of Words Intro">
</div>

<br>

> **"Uma selva de caracteres complexos, domada de forma instantânea pela Inteligência Artificial."**

## 🎯 O Problema (A Dor)
Em ambientes de alta demanda operacional, a resolução manual de verificações de segurança visuais (Captchas) baseados em texto se torna um gigantesco gargalo de produtividade. O esforço repetitivo não apenas fatiga o operador, mas também trava o fluxo de trabalho contínuo. 

Antes dessa solução, um operador focado era capaz de realizar em média **100 consultas por dia**. Com a implantação da máquina do **Jungle of Words**, o tempo ocioso e de digitação foi aniquilado, permitindo um aumento impressionante de **150% na produção diária**.

---

## 🧠 Por que não usar Inteligência Artificial de Nuvem? (A Solução)
Hoje em dia, com o avanço de Modelos de Linguagem de Grande Escala (LLMs) como a API do Google Gemini Pro Vision ou ChatGPT-4V, seria totalmente possível enviar essas imagens e pedir a leitura por IA. No entanto, o uso corporativo dessas APIs em massa possui duas desvantagens cruciais:

1. **Custo Operacional Constante:** APIs de visão computacional de ponta são tarifadas. O custo (em dólares) por cada requisição de imagem processada pode escalar brutalmente quando falamos de milhares de interações diárias.
2. **Latência de Rede:** Enviar uma imagem pela internet para o servidor da IA e aguardar a resposta leva um tempo médio de 3 a 5 segundos por operação.

A nossa abordagem é oposta: **100% Offline, Zero Custos e Alta Velocidade.**  
O *Jungle of Words* processa e classifica toda a matriz de pixels localmente, sem depender de internet, entregando a resposta pronta em **menos de 1 segundo**.

---

## ⚙️ Como Funciona a Engenharia? (O K-Nearest Neighbors)

A ferramenta não "chuta" as respostas através de algoritmos heurísticos falhos. Ela possui um "cérebro" treinado localmente usando Visão Computacional Avançada e o algoritmo matemático **KNN (K-Nearest Neighbors)**.

<div align="center">
  <img src="controle_jungle.png" alt="Interface de Operação (Jungle Console)" width="800">
</div>

### O Fluxo de Execução
1. **Captura em Tempo Real:** Ao invés de o usuário ter que baixar e subir arquivos, ele simplesmente aperta o atalho de teclado global `Ctrl+Alt+S`. A tela escurece e abre uma interface limpa de "Recorte" (Snipping Tool).
2. **Corte e Fatiamento Cirúrgico:** O usuário clica e arrasta sobre o enigma visual. O algoritmo (usando OpenCV) recebe a imagem, converte em escalas de cinza, limpa os ruídos indesejados, inverte a paleta e rastreia os contornos físicos para "fatiar" cada caractere solto em um bloco individual de pixels.
3. **Classificação via Memória (KNN):** Cada letra fatiada é convertida em um formato padrão `32x32`, transformada num vetor numérico gigantesco e comparada simultaneamente contra milhares de outros exemplos de caracteres no nosso Banco de Memória offline. O algoritmo procura o "vizinho numérico mais próximo" para confirmar com 99% de precisão de qual letra se trata.
4. **Clipboard Automático:** Em milissegundos, a palavra completa é injetada na Área de Transferência do sistema (`Ctrl+C`), enquanto emite um aviso sonoro (Bip) de sucesso!

<div align="center">
  <img src="captcha_photo.png" alt="Exemplo prático de Captcha Lida" width="600">
</div>

---

## 🚀 Como Executar o Software Comercial

Esse projeto não é apenas um script, mas um software empacotado e compilado de forma industrial em um arquivo `.exe`. O seu computador não precisa de bibliotecas nem do Python instalado.

1. Navegue até a pasta de distribuição oficial (`dist/Jungle_of_Words`).
2. Dê um duplo clique mágico no arquivo **`Jungle_of_Words.exe`**.
3. A nossa interface "Jungle Console" gráfica abrirá ostentando a arte visual de abertura.
4. Pressione `ENTER` no terminal para ligar os motores.
5. Deixe a janela rodando ou minimizada no fundo! Sempre que esbarrar em um obstáculo de texto, pressione **`Ctrl+Alt+S`**, selecione e cole a resposta mágica (`Ctrl+V`).

---

## 🛠 Tecnologias Utilizadas

- **Python 3.x:** A base da arquitetura.
- **OpenCV (`cv2`):** Responsável por todo o pipeline de Visão Computacional (Threshold adaptativo, componentes conectados para limpeza e algoritmo de predição KNN).
- **NumPy:** Base matemática para manipulação dos blocos de pixels.
- **Tkinter:** Biblioteca nativa usada tanto para emular o nosso glorioso Terminal Hacker ("Jungle Console") quanto para sobrepor a tela na ferramenta de captura visual.
- **PyInstaller:** Compilador e integrador utilizado para gerar a build final, embutindo o banco de dados e imagens no Payload executável do Windows.
