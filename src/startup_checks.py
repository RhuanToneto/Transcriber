from pathlib import Path
import subprocess
import shutil
import sys


def obter_pasta_projeto():
    """
    Retorna o caminho da pasta raiz do projeto (um nível acima de 'src').
    """
    return Path(__file__).parent.parent.absolute()


def _criar_e_ocultar(path: Path, content: str = ""):
    """
    Cria um arquivo com o conteúdo fornecido e, no Windows, marca-o como oculto.

    Usado para criar arquivos de controle como '.gitkeep' e '.gitignore'.
    """
    try:
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            path.write_text(content, encoding='utf-8')

        # Em Windows, define o atributo de arquivo como oculto
        if sys.platform.startswith("win"):
            subprocess.run(["attrib", "+h", str(path)], check=True, capture_output=True)
    except Exception:
        raise


def verificar_prerequisitos():
    """
    Verifica se o ffmpeg está disponível e garante que as pastas
    essenciais do projeto existam (criando-as se necessário).

    Retorna True se tudo estiver OK, False se o ffmpeg não for encontrado.
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        try:
            # Tenta executar 'ffmpeg -version' para confirmar presença
            resultado = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
            if resultado.returncode != 0:
                raise Exception("FFmpeg not found")
        except Exception:
            # Informa o usuário com instruções de instalação no Windows
            print()
            print(r"""        
❌ FFmpeg não encontrado

🛠️  Como resolver:
1. Baixe o FFmpeg para Windows no site oficial: https://ffmpeg.org/download.html
2. Descompacte o arquivo ZIP em uma pasta (ex.: C:\ffmpeg).
3. Adicione a pasta 'bin' ao PATH do Windows:
   - Abra o menu Iniciar e pesquise por "Editar variáveis de ambiente do sistema".
   - Clique em "Variáveis de ambiente".
   - Em "Variáveis do sistema", selecione "Path" > "Editar" > "Novo".
   - Cole o caminho da pasta 'bin' (ex.: C:\ffmpeg\bin).
   - Confirme as alterações clicando em "OK".
""".strip())
            return False

    pasta_projeto = obter_pasta_projeto()
    pastas_essenciais = {
        "videos": pasta_projeto / "videos",
        "models": pasta_projeto / "models",
        "transcripts": pasta_projeto / "transcripts",
        "temp_audios": pasta_projeto / "temp_audios",
    }

    for nome, pasta in pastas_essenciais.items():
        try:
            if not pasta.exists():
                pasta.mkdir(parents=True, exist_ok=True)
            gitkeep = pasta / ".gitkeep"
            _criar_e_ocultar(gitkeep, "")
        except Exception:
            raise

    try:
        gitignore_path = pasta_projeto / ".gitignore"
        gitignore_content = (
            "models/*\n"
            "!models/.gitkeep\n"
            "\n"
            "__pycache__/\n"
            "\n"
            "temp_audios/*\n"
            "!temp_audios/.gitkeep\n"
            "\n"
            "transcripts/*\n"
            "!transcripts/.gitkeep\n"
            "\n"
            "videos/*\n"
            "!videos/.gitkeep\n"
        )
        _criar_e_ocultar(gitignore_path, gitignore_content)
    except Exception:
        raise

    return True
