from pathlib import Path
from src.utils import confirmar_acao


FORMATOS_VIDEO_SUPORTADOS = (
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm',
    '.flv', '.m4v', '.mpg', '.mpeg', '.ts', '.3gp'
)


def obter_pasta_projeto():
    """
    Retorna a pasta raiz do projeto.
    """
    return Path(__file__).parent.parent.absolute()


def encontrar_videos():
    """
    Lista arquivos de vídeo presentes na pasta 'videos/' que tenham
    extensões suportadas.

    Retorna uma lista de nomes de arquivo (strings), ordenada.
    """
    pasta_projeto = obter_pasta_projeto()
    pasta_videos = pasta_projeto / "videos"
    
    if not pasta_videos.exists():
        return []
    
    videos_encontrados = []
    
    try:
        for arquivo in pasta_videos.iterdir():
            # Verifica se é arquivo e se a extensão está na lista suportada
            if arquivo.is_file() and arquivo.suffix.lower() in FORMATOS_VIDEO_SUPORTADOS:
                videos_encontrados.append(arquivo.name)
    except Exception:
        # Propaga exceção para o chamador lidar com problemas de I/O
        raise
    
    videos_encontrados.sort()
    
    return videos_encontrados


def obter_nomes_videos():
    """Alias para encontrar_videos() usado pelo programa principal."""
    return encontrar_videos()


def analisar_status_videos(nomes_videos):
    """
    Para cada vídeo da lista, verifica se já existe um arquivo
    de transcrição correspondente em 'transcripts/'.

    Retorna duas listas: (nao_transcritos, ja_transcritos)
    contendo os nomes dos arquivos.
    """
    pasta_transcripts = obter_pasta_projeto() / "transcripts"
    nao_transcritos = []
    ja_transcritos = []
    for nome_video in nomes_videos:
        nome_base = Path(nome_video).stem
        arquivo_transcricao = pasta_transcripts / f"{nome_base}.txt"
        if arquivo_transcricao.exists():
            ja_transcritos.append(nome_video)
        else:
            nao_transcritos.append(nome_video)
    return nao_transcritos, ja_transcritos


def confirmar_processamento_inteligente(videos_nao_transcritos, videos_ja_transcritos):
    """
    Mostra ao usuário uma lista de vídeos não transcritos e já transcritos
    e pergunta como proceder:
      - somente não transcritos (recomendado)
      - todos (reprocessa existentes)
      - cancelar

    Retorna uma tupla booleana (incluir_nao_transcritos, incluir_ja_transcritos).
    """
    cnt_nao = len(videos_nao_transcritos)
    if cnt_nao > 0:
        label = "Vídeo não transcrito" if cnt_nao == 1 else "Vídeos não transcritos"
        print(f"🆕 {label} ({cnt_nao}):")
        for i, nome in enumerate(videos_nao_transcritos, 1):
            print(f"   {i:2d}. {nome}")
        print()
    cnt_ja = len(videos_ja_transcritos)
    if cnt_ja > 0:
        label = "Vídeo já transcrito" if cnt_ja == 1 else "Vídeos já transcritos"
        print(f"✅ {label} ({cnt_ja}):")
        for i, nome in enumerate(videos_ja_transcritos, 1):
            print(f"   {i:2d}. {nome}")
        print()
    if cnt_nao > 0 and cnt_ja > 0:
        # Se houver ambos, oferece opções explícitas ao usuário
        print("📋 OPÇÕES:")
        print("   [1] Apenas vídeos sem transcrição (RECOMENDADO)")
        print("   [2] Todos os vídeos (Reprocessa transcrições existentes)")
        print("   [3] Cancelar")
        while True:
            resposta = input("\n❓ Escolha uma opção [1, 2 ou 3]: ").strip()
            if resposta == "1":
                return True, False
            elif resposta == "2":
                return True, True
            elif resposta == "3":
                # Cancela a operação levantando KeyboardInterrupt para o fluxo principal
                raise KeyboardInterrupt()
            else:
                print("   ❌ Opção inválida. Digite 1, 2 ou 3")
    elif len(videos_nao_transcritos) > 0:
        # Só há vídeos não transcritos: pergunta confirmação simples
        cnt = len(videos_nao_transcritos)
        item = "vídeo" if cnt == 1 else "vídeos"
        estado = "não transcrito" if cnt == 1 else "não transcritos"
        if confirmar_acao(f"❓ Transcrever {cnt} {item} {estado}?"):
            return True, False
        else:
            return False, False
    elif len(videos_ja_transcritos) > 0:
        # Só há vídeos já transcritos: pergunta se reprocessa
        cnt = len(videos_ja_transcritos)
        item = "vídeo" if cnt == 1 else "vídeos"
        estado = "já transcrito" if cnt == 1 else "já transcritos"
        if confirmar_acao(f"❓ Transcrever novamente {cnt} {item} {estado}?"):
            return False, True
        else:
            return False, False
    return False, False


def informar_pasta_videos_vazia():
    """
    Informa ao usuário que a pasta 'videos/' está vazia e mostra os formatos suportados.
    """
    print("\n📂 Nenhum vídeo encontrado")
    formatos = ', '.join(map(str, FORMATOS_VIDEO_SUPORTADOS))
    print("\n💡 Coloque vídeos na pasta 'videos/' para começar as transcrições")
    print(f"📹 Formatos suportados: {formatos}")
    return True
