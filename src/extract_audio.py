import subprocess
from pathlib import Path


# Configurações de áudio usadas na extração
AUDIO_SAMPLE_RATE = 16000  # taxa de amostragem (Hz)
AUDIO_CHANNELS = 1         # mono
AUDIO_FORMAT = "wav"     # formato do arquivo de saída
AUDIO_CODEC = "pcm_s16le"  # codec para WAV PCM 16-bit


def obter_pasta_projeto():
    """
    Retorna o caminho da pasta raiz do projeto (um nível acima de 'src').
    """
    return Path(__file__).parent.parent.absolute()


def extrair_audio(video_path, audio_path):
    """
    Usa o ffmpeg para extrair a faixa de áudio de um arquivo de vídeo.

    Parâmetros:
      - video_path: Path para o arquivo de vídeo de entrada.
      - audio_path: Path para salvar o arquivo de áudio de saída.

    Retorna True se a extração for bem-sucedida e o arquivo gerado tiver conteúdo.
    """
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    comando = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",  # desativa fluxo de vídeo
        "-acodec", AUDIO_CODEC,
        "-ar", str(AUDIO_SAMPLE_RATE),
        "-ac", str(AUDIO_CHANNELS),
        "-y",  # sobrescreve sem perguntar
        str(audio_path)
    ]

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=600
        )

        # Verifica retorno do ffmpeg e se o arquivo foi criado com tamanho > 0
        if resultado.returncode == 0:
            if audio_path.exists() and audio_path.stat().st_size > 0:
                return True
            else:
                return False
        else:
            return False
    except Exception:
        # Propaga exceção para o chamador lidar com falhas inesperadas
        raise


def extrair_audio_do_video(nome_video):
    """
    Conveniência: recebe o nome do arquivo de vídeo na pasta 'videos/'
    e tenta extrair o áudio para 'temp_audios/' retornando o caminho.

    Retorna (True, caminho_arquivo) em sucesso ou (False, None) em falha.
    """
    pasta_projeto = obter_pasta_projeto()
    pasta_videos = pasta_projeto / "videos"
    pasta_audios = pasta_projeto / "temp_audios"
    video_path = pasta_videos / nome_video
    nome_base = Path(nome_video).stem
    if not video_path.exists():
        return False, None
    audio_path = pasta_audios / f"{nome_base}.{AUDIO_FORMAT}"
    sucesso = extrair_audio(video_path, audio_path)
    if sucesso:
        return True, audio_path
    else:
        return False, None
