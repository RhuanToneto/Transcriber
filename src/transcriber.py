import time
import whisper
import warnings
import sys
import gc
from pathlib import Path
from .loading_spinner import SpinnerCarregamento
from .utils import plural, formatar_duracao
from src import extract_audio
from src import cleanup

# Suprime avisos do módulo whisper para manter a saída limpa
warnings.filterwarnings("ignore", category=UserWarning, module="whisper")

# -------------------------------
# Configurações do modelo e transcrição
# -------------------------------
MODEL_SIZE = "medium"  # Tamanho do modelo (ex.: tiny, base, small, medium, large)

LANGUAGE = None  # Define idioma; None permite detecção automática

TEMPERATURE = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)

NO_SPEECH_THRESHOLD = 0.5

LOGPROB_THRESHOLD = -0.8

COMPRESSION_RATIO_THRESHOLD = 2.0

BEAM_SIZE = None
BEST_OF = None

CONDITION_ON_PREVIOUS_TEXT = True
INITIAL_PROMPT = None
HALLUCINATION_SILENCE_THRESHOLD = None

PATIENCE = None
LENGTH_PENALTY = None
SUPPRESS_TOKENS = "-1"
SUPPRESS_BLANK = True
MAX_INITIAL_TIMESTAMP = 1.0

WORD_TIMESTAMPS = True
VERBOSE = False
FP16 = False

# Variável que guarda o modelo carregado em memória
_modelo_carregado = None


def obter_pasta_projeto():
    """
    Retorna a pasta raiz do projeto (um nível acima de 'src').
    """
    return Path(__file__).parent.parent.absolute()


def configurar_diretorio_modelo():
    """
    Garante que a pasta 'models/' exista e retorna seu caminho como string.
    O whisper pode usar este caminho para armazenar/ler os arquivos do modelo.
    """
    pasta_projeto = obter_pasta_projeto()
    pasta_models_path = pasta_projeto / "models"

    pasta_models_path.mkdir(parents=True, exist_ok=True)

    return str(pasta_models_path)


def limpar_modelo():
    """
    Libera o modelo carregado da memória, se existir.
    Útil para liberar RAM/VRAM entre execuções.
    """
    global _modelo_carregado

    if _modelo_carregado is None:
        return True

    del _modelo_carregado
    _modelo_carregado = None
    import gc
    gc.collect()
    return True


def obter_modelo():
    """Retorna o objeto do modelo já carregado (ou None)."""
    global _modelo_carregado
    return _modelo_carregado


def carregar_modelo():
    """
    Carrega (ou retorna) o modelo do whisper configurado em MODEL_SIZE.

    Se o modelo já estiver carregado, retorna imediatamente. Caso contrário,
    tenta carregar da pasta 'models' e exibe um spinner enquanto carrega.
    """
    global _modelo_carregado
    
    if _modelo_carregado is not None:
        return _modelo_carregado

    pasta_models = configurar_diretorio_modelo()

    caminho_modelo_pt = Path(pasta_models) / f"{MODEL_SIZE}.pt"

    try:
        if caminho_modelo_pt.exists():
            print("📦 Modelo encontrado")
            spinner = SpinnerCarregamento("🤖 Carregando modelo...")
            spinner.start()

            modelo = whisper.load_model(
                MODEL_SIZE,
                device="cpu",
                download_root=pasta_models
            )

            spinner.stop()
            print("✅ Modelo carregado\n")
        else:
            # Se o arquivo do modelo não existir, o whisper fará o download
            print("🔎 Modelo não encontrado. Baixando...")
            modelo = whisper.load_model(
                MODEL_SIZE,
                device="cpu",
                download_root=pasta_models
            )
            print("✅ Download concluído")
            print("✅ Modelo carregado\n")

        _modelo_carregado = modelo
        return modelo
    except KeyboardInterrupt:
        # Garante parada limpa do spinner em caso de interrupção do usuário
        if 'spinner' in locals():
            spinner.stop()
        raise
    except Exception:
        if 'spinner' in locals():
            spinner.stop()
        _modelo_carregado = None
        raise


def transcrever_audio(audio_path, nome_base):
    """
    Executa a transcrição de um arquivo de áudio usando o modelo carregado.

    - audio_path: Path para o arquivo .wav
    - nome_base: nome do vídeo/arquivo de origem (usado para salvar o .txt)
    """
    modelo = carregar_modelo()

    print(f"📝 Transcrevendo: {audio_path.name}")

    tempo_inicio = time.time()

    resultado = modelo.transcribe(
        str(audio_path),
        language=LANGUAGE,
        temperature=TEMPERATURE,
        no_speech_threshold=NO_SPEECH_THRESHOLD,
        logprob_threshold=LOGPROB_THRESHOLD,
        compression_ratio_threshold=COMPRESSION_RATIO_THRESHOLD,
        condition_on_previous_text=CONDITION_ON_PREVIOUS_TEXT,
        initial_prompt=INITIAL_PROMPT,
        hallucination_silence_threshold=HALLUCINATION_SILENCE_THRESHOLD,
        word_timestamps=WORD_TIMESTAMPS,
        verbose=VERBOSE,
        beam_size=BEAM_SIZE,
        best_of=BEST_OF,
        patience=PATIENCE,
        length_penalty=LENGTH_PENALTY,
        suppress_tokens=SUPPRESS_TOKENS,
        suppress_blank=SUPPRESS_BLANK,
        max_initial_timestamp=MAX_INITIAL_TIMESTAMP,
        fp16=FP16
    )

    tempo_total = time.time() - tempo_inicio
    tempo_formatado = formatar_duracao(tempo_total)

    texto_transcrito = resultado["text"].strip()
    print(f"🕒 Tempo da transcrição: {tempo_formatado}")

    # Salva o texto transcrito em 'transcripts/{nome_base}.txt'
    pasta_transcripts = obter_pasta_projeto() / "transcripts"
    pasta_transcripts.mkdir(parents=True, exist_ok=True)
    nome_base_sem_ext = Path(nome_base).stem
    arquivo_resultado = pasta_transcripts / f"{nome_base_sem_ext}.txt"

    with open(arquivo_resultado, "w", encoding="utf-8") as f:
        f.write(texto_transcrito)

    print(f"💾 Transcrição salva: {arquivo_resultado.name}")
    return True


def transcrever_video(nome_base):
    """
    Fluxo de transcrição para um vídeo:
      1) extrai áudio para 'temp_audios/'
      2) transcreve o áudio
      3) remove o arquivo de áudio temporário
    """
    print("\n🎵 [1/2] EXTRAINDO ÁUDIO")
    sucesso_extracao, caminho_audio = extract_audio.extrair_audio_do_video(nome_base)
    
    if not sucesso_extracao:
        return False
    
    print(f"✅ Áudio extraído com sucesso\n")
    
    try:
        print("📝 [2/2] TRANSCREVENDO ÁUDIO")
        sucesso_transcricao = transcrever_audio(caminho_audio, nome_base)

        if not sucesso_transcricao:
            return False

        print(f"✅ Transcrição concluída com sucesso\n")

        _ = cleanup.limpar_audio(caminho_audio)
        return True
    finally:
        # Garante remoção do arquivo temporário mesmo em caso de erro
        try:
            if 'caminho_audio' in locals() and caminho_audio is not None:
                _ = cleanup.limpar_audio(caminho_audio)
        except Exception:
            raise
