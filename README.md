# Transcritor

Este projeto é uma aplicação em Python que automatiza a transcrição de vídeos utilizando modelos de reconhecimento de fala. O sistema permite ao usuário selecionar vídeos, extrair o áudio com FFmpeg e gerar transcrições precisas por meio do modelo Whisper da OpenAI.

A interface é baseada em linha de comando, guiando o usuário desde a verificação de pré-requisitos até o processamento dos arquivos. O programa organiza os vídeos, áudios temporários e transcrições em pastas dedicadas, facilitando o gerenciamento dos dados. Recursos adicionais incluem limpeza automática de arquivos temporários, seleção inteligente de vídeos para transcrição e relatórios detalhados sobre o processamento.

## Requisitos

- [Python 3.10+](https://www.python.org/downloads/)  (Recomendado).
- [FFmpeg](https://ffmpeg.org/download.html) instalado e acessível via PATH.

### Instalação do FFmpeg (Windows)

1. Baixe o FFmpeg para Windows no site oficial: https://ffmpeg.org/download.html
2. Descompacte o arquivo ZIP em uma pasta (ex.: C:\ffmpeg).
3. Adicione a pasta 'bin' ao PATH do Windows:
     - Abra o menu Iniciar e pesquise por "Editar variáveis de ambiente do sistema".
     - Clique em "Variáveis de ambiente".
     - Em "Variáveis do sistema", selecione "Path" > "Editar" > "Novo".
     - Cole o caminho da pasta 'bin' (ex.: C:\ffmpeg\bin).
     - Confirme as alterações clicando em "OK".

## Como Usar

### **Baixe o zip ou clone o repositório**

1. Instale as dependências:

   ```
   python -m pip install -r requirements.txt
   ```

2. Coloque os vídeos dentro da pasta [videos](videos).

3. Execute o programa:

   ```
   python main.py
   ```

Siga as instruções no terminal.
