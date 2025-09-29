from pathlib import Path


def limpar_audio(audio_path):
    """
    Remove um arquivo de áudio se existir.

    Entrada:
      - audio_path: caminho (Path ou str) para o arquivo de áudio.

    Retorno:
      - True em caso de sucesso ou se 'audio_path' for None.
    """
    if audio_path is None:
        return True

    if isinstance(audio_path, str):
        audio_path = Path(audio_path)

    if not isinstance(audio_path, Path):
        audio_path = Path(str(audio_path))

    try:
        # missing_ok evita erro se o arquivo não existir (Python 3.8+)
        audio_path.unlink(missing_ok=True)
        return True
    except Exception:
        # Propaga a exceção para o chamador tratar
        raise


def limpar_temp_audios():
    """
    Remove arquivos .wav dentro da pasta 'temp_audios' do projeto.

    Retorna o número de arquivos removidos.
    """
    try:
        pasta_projeto = Path(__file__).parent.parent.absolute()
        pasta_temp_audios = pasta_projeto / "temp_audios"
        if not pasta_temp_audios.exists():
            return 0
        arquivos_removidos = 0
        for arquivo in pasta_temp_audios.glob("*.wav"):
            if arquivo.is_file():
                try:
                    arquivo.unlink()
                    arquivos_removidos += 1
                except Exception:
                    # Propaga exceção se não for possível remover um arquivo
                    raise
        return arquivos_removidos
    except Exception:
        raise


def limpar_pycache():
    """
    Percorre o projeto e remove pastas '__pycache__' junto com seus arquivos.

    Retorna quantas pastas '__pycache__' foram removidas.
    """
    pasta_projeto = Path(__file__).parent.parent.absolute()
    removidos = 0
    for caminho in pasta_projeto.rglob("__pycache__"):
        try:
            if caminho.is_dir():
                for item in caminho.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                    except Exception:
                        # Propaga em caso de falha ao remover arquivos internos
                        raise
                try:
                    caminho.rmdir()
                    removidos += 1
                except Exception:
                    # Propaga se não for possível remover a pasta
                    raise
        except Exception:
            raise
    return removidos
