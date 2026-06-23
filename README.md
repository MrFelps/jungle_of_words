# Jungle of Words 🌴

<img width="1536" height="1024" alt="intro" src="https://github.com/user-attachments/assets/c761724c-0376-4b07-9755-88bfd94f0dbf" />


> **"Uma selva de caracteres complexos, domada de forma instantânea pela Inteligência Artificial e Visão Computacional."**

## 🎯 O Problema: A Dor da Operação Manual
Em cenários de alta demanda operacional, a resolução manual de verificações de segurança visuais (Captchas) baseados em texto frequentemente se apresenta como um severo gargalo de produtividade. O esforço contínuo e repetitivo não apenas induz à fadiga da operação, mas também fragmenta o fluxo de trabalho automatizado.

Antes da implementação desta arquitetura, a capacidade média de processamento situava-se na marca de **100 consultas diárias por operador**. Com a introdução do motor inteligente do **Jungle of Words**, o tempo de ociosidade e as intervenções manuais de digitação foram mitigados quase integralmente, viabilizando um salto de **150% na eficiência e produtividade diária**.

---

## 🧠 Abordagem Híbrida: Processamento Local vs. Cloud APIs
Atualmente, a integração com Modelos de Visão e Linguagem de Grande Escala (LLMs), como a API do Google Gemini Pro Vision ou ChatGPT-4V, representa um caminho viável para a solução de enigmas visuais. Contudo, a aplicação comercial dessas APIs em regime de alto tráfego encontra dois atritos fundamentais:

1. **Escalabilidade de Custos:** APIs de visão computacional corporativas operam sob tarifação por requisição. Em um ecossistema com milhares de interações diárias, o custo diluído por operação compromete severamente a viabilidade financeira da automação contínua.
2. **Latência Inerente:** A dependência da infraestrutura de rede para o tráfego bidirecional das matrizes de imagem aos servidores remotos adiciona uma latência indesejada (em média 3 a 5 segundos por transação).

A arquitetura do *Jungle of Words* contorna esses limitadores adotando uma estratégia oposta: **Processamento 100% Offline, Otimização Estrutural (Zero Cost API) e Ultra Baixa Latência.**  
O motor compila e classifica toda a matriz vetorial da imagem de forma nativa e em ambiente fechado, entregando a string de dados estruturada diretamente na área de transferência do usuário em **menos de 1 segundo**.

---

## 🔬 Arquitetura Técnica: Um "Deep Dive" no Pipeline

Para atingir a precisão e a velocidade de uma leitura em tempo real sem depender de APIs externas, a arquitetura do projeto foi dividida em um Pipeline de 4 estágios matemáticos precisos:

<img width="848" height="726" alt="controle_jungle" src="https://github.com/user-attachments/assets/efc18aec-80cd-4b8a-bd2c-0af5600a9f22" />

### 1. Interceptação e Captura (Snipping Tool)
O usuário aciona o atalho global de teclado (`Ctrl+Alt+S`). Nesse exato milissegundo:
- A biblioteca `PIL.ImageGrab` tira um print silencioso da tela inteira em memória.
- O `Tkinter` (Frontend) abre uma janela *borderless* e *fullscreen* com `alpha=0.3` (transparente), congelando a tela visualmente e transformando o cursor em uma cruz.
- Algoritmos de geometria baseados em eventos de mouse desenham um *Bounding Box* dinâmico que o usuário recorta.

### 2. Tratamento e Limpeza de Ruído (Computer Vision)
O pedaço de imagem recortado é injetado no motor do **OpenCV**.
- **Conversão de Domínio:** A imagem BGR é convertida em escalas de cinza (1 canal) e isolamos apenas a camada mais densa usando `np.min(axis=2)`.
- **Thresholding Adaptativo:** Ao invés de binarização simples, usamos `cv2.adaptiveThreshold` para calcular a iluminação da imagem de forma regional. Isso impede que sombras na tela destruam a leitura da letra.
- **Isolamento de Componentes (Despoluição):** Usamos a função matemática `connectedComponentsWithStats` para varrer os "agrupamentos de pixels". Todo e qualquer borrão de poeira ou risco que tenha uma área (`CC_STAT_AREA`) menor do que 25 pixels é brutalmente apagado, deixando o fundo imaculado.

### 3. Fatiamento Cirúrgico (Character Segmentation)
Com a imagem limpa, precisamos separar palavra por palavra.
- Varremos novamente os componentes conectados em busca de contornos. Desenhamos blocos matemáticos (`X, Y, Width, Height`) em volta de cada mancha preta.
- **Fusão de Blocos Sobrepostos:** Algumas fontes de letras possuem quebras no meio (como o pingos do "i" ou "j"). O nosso algoritmo possui uma heurística geométrica que verifica se dois retângulos se cruzam no eixo vertical. Se a sobreposição for maior que 30%, ele unifica os blocos, tratando a letra como uma entidade única.
- O OpenCV corta (`slice`) a matriz da imagem exata onde cada letra está, transformando uma palavra em dezenas de matrizes menores de caracteres independentes.

### 4. Machine Learning KNN (K-Nearest Neighbors)
É aqui que a mágica offline acontece. 
- Cada imagem de caractere recortada é redimensionada à força para a dimensão padrão de `32x32` pixels e as cores são invertidas (`bitwise_not`).
- A matriz 2D é "achatada" (`flatten()`), tornando-se um vetor numérico unidimensional de exatos **1024 atributos (features)**.
- O OpenCV (`cv2.ml.KNearest_create()`) compara esse vetor matematicamente (usando distância euclidiana) contra **dezenas de milhares** de outras imagens que nós rotulamos e treinamos localmente e injetamos na memória do `.exe`.
- Ele busca o "Vizinhança mais próxima" (`K=1`) no hiperespaço e nos devolve a resposta final: "Esta imagem é a letra B".

### 5. Injeção Direta
A resposta em texto passa por um `join()`, é colada de forma invisível direto na memória RAM do seu Sistema Operacional usando a biblioteca `pyperclip` e o sistema dispara um sinal ultrassônico nativo (`winsound.Beep`) confirmando a conclusão.

<img width="420" height="151" alt="captcha_photo" src="https://github.com/user-attachments/assets/c52eb50e-1356-494e-bdce-2947abc9de3c" />

---

## 🚀 Como Executar o Software Comercial

Esse projeto não é apenas um script, mas um software empacotado e compilado de forma industrial em um arquivo `.exe`. O seu computador não precisa de bibliotecas nem do Python instalado.

1. Navegue até a pasta de distribuição oficial (`dist/Jungle_of_Words`).
2. Dê um duplo clique mágico no arquivo **`Jungle_of_Words.exe`**.
3. A nossa interface "Jungle Console" gráfica abrirá ostentando a arte visual de abertura.
4. Pressione `ENTER` no terminal para ligar os motores.
5. Deixe a janela rodando ou minimizada no fundo! Sempre que esbarrar em um obstáculo de texto, pressione **`Ctrl+Alt+S`**, selecione e cole a resposta mágica (`Ctrl+V`).

---

## 🛠 Stack de Bibliotecas e Dependências Técnicas

Abaixo as ferramentas diretas que foram instaladas no ambiente isolado (Python 3.14+) para fabricar o sistema de ponta a ponta:

* **`opencv-python` (cv2):** O coração da Inteligência Artificial. Fornece tanto os algoritmos de processamento de matriz (Binarização, Connected Components) quanto o modelo de classificação matemática de aprendizado de máquina KNN (Machine Learning Module).
* **`numpy`:** Motor matemático que opera por trás das imagens. Utilizado incessantemente para reordenamento matricial `array[::-1]`, operações `axis=2` e montagem de vetores de alta flutuação (`np.float32`) para consumo da IA.
* **`Pillow` (PIL):** Utilizada especificamente pelo módulo `ImageGrab.grab()` para capturar o frame raw (bruto) da memória de vídeo da placa-mãe na hora que a tela é congelada para recorte. E `ImageTk` para exibição HD do Terminal Console.
* **`keyboard`:** Sistema de KeyHook global em baixo nível de sistema operacional (Windows API) para interceptar o `Ctrl+Alt+S` de forma passiva no fundo, independente do software que estiver focado em primeiro plano.
* **`pyperclip`:** Ponte de injeção direta de texto na área de transferência binária do Windows OS, para o *Ctrl+C* instantâneo.
* **`tkinter`:** Biblioteca GUI Nativa de renderização que desenha nosso Frontend emulado. Foi subvertido da sua função padrão para agir como um terminal de terminal (`ScrolledText`) recebendo fluxos binários do backend.
* **`pyinstaller`:** Arquitetura de Empacotamento. Envolve o nosso sistema inteiro em um *Bootloader* do Windows (CArchive), embutindo as DLLs nativas e injetando nosso Banco de Treinamento KNN (`renomeada/`) diretamente no *Payload* do executável usando ponteiros `sys._MEIPASS`.
