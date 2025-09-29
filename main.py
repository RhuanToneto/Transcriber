import sys
import time
from pathlib import Path
from src import cleanup
from src import extract_audio
from src import list_videos
from src import startup_checks
from src import transcriber
from src.utils import plural, confirmar_acao, exibir_cabecalho, formatar_duracao
from src.list_videos import analisar_status_videos, confirmar_processamento_inteligente


def obter_pasta_projeto():
    # Retorna a pasta raiz do projeto (delegando a startup_checks)
    from src.startup_checks import obter_pasta_projeto as _obter_pasta
    return _obter_pasta()


def verificar_prerequisitos():
    # Verifica FFmpeg e cria pastas essenciais se necessário
    return startup_checks.verificar_prerequisitos()


def processar_video_individual(nome_base):
    # Fluxo de processamento para um único vídeo (extrair + transcrever)
    return transcriber.transcrever_video(nome_base)


def processar_todos_videos():
    # Busca todos os vídeos na pasta 'videos/' e decide quais processar
    nomes_videos = list_videos.obter_nomes_videos()
    if not nomes_videos:
        list_videos.informar_pasta_videos_vazia()
        return 0, 0, False
    total_videos = len(nomes_videos)
    print(f"\n🎬 Total de vídeos encontrados: {total_videos} {plural(total_videos, 'Vídeo', 'Vídeos')}\n")
    # Separa vídeos que já têm transcrição daqueles que não têm
    nao_transcritos, ja_transcritos = analisar_status_videos(nomes_videos)
    # Pergunta ao usuário como proceder (apenas novos / todos / cancelar)
    incluir_nao_transcritos, incluir_ja_transcritos = confirmar_processamento_inteligente(nao_transcritos, ja_transcritos)
    if not incluir_nao_transcritos and not incluir_ja_transcritos:
        return 0, 0, True
    lista_para_transcrever = []
    if incluir_nao_transcritos:
        lista_para_transcrever.extend(nao_transcritos)
    if incluir_ja_transcritos:
        lista_para_transcrever.extend(ja_transcritos)
    # Executa o processamento em sequência e acumula estatísticas
    sucessos = 0
    tempo_inicio = time.time()
    hora_inicio = time.strftime("%H:%M:%S", time.localtime(tempo_inicio))
    dia_inicio = time.strftime("%d/%m/%Y", time.localtime(tempo_inicio))
    for i, nome_base in enumerate(lista_para_transcrever, 1):
        exibir_cabecalho(f"🔄 VÍDEO {i}/{len(lista_para_transcrever)} - {nome_base}")
        try:
            sucesso = processar_video_individual(nome_base)
            if sucesso:
                sucessos += 1
            else:
                break
        except KeyboardInterrupt:
            # Permite que o usuário cancele todo o processo via Ctrl+C
            raise
        except Exception:
            # Propaga exceções inesperadas para diagnóstico
            raise
    tempo_fim = time.time()
    hora_fim = time.strftime("%H:%M:%S", time.localtime(tempo_fim))
    dia_fim = time.strftime("%d/%m/%Y", time.localtime(tempo_fim))
    tempo_total = time.time() - tempo_inicio
    tempo_formatado = formatar_duracao(tempo_total)
    # Exibe relatório final com tempo e arquivos salvos
    exibir_cabecalho("📊 RELATÓRIO FINAL")
    if dia_inicio == dia_fim:
        print(f"\n📅 Início: {hora_inicio} | Fim: {hora_fim}")
    else:
        print(f"\n📅 Início: {hora_inicio} {dia_inicio} | Fim: {hora_fim} {dia_fim}")
    print(f"🕒 Tempo total: {tempo_formatado}")
    pasta_transcripts = obter_pasta_projeto() / "transcripts"
    arquivos_salvos = []
    for nome in lista_para_transcrever:
        nome_stem = Path(nome).stem
        arquivo_transcricao = pasta_transcripts / f"{nome_stem}.txt"
        if arquivo_transcricao.exists():
            arquivos_salvos.append(arquivo_transcricao.name)

    transcricoes_concluidas = len(arquivos_salvos)
    label = plural(transcricoes_concluidas, 'transcrição concluída', 'transcrições concluídas')
    print(f"✅ {transcricoes_concluidas} {label}")

    if arquivos_salvos:
        header = f"💾 {plural(transcricoes_concluidas, 'Transcrição salva', 'Transcrições salvas')} na pasta: transcripts/"
        print(f"\n{header}")
        for filename in arquivos_salvos:
            print(f"   📄 {filename}")

    return len(lista_para_transcrever), transcricoes_concluidas, False


def main():
    try:               
        # Ponto de entrada principal: exibe cabeçalho, checa pré-requisitos
        exibir_cabecalho()
        
        if not verificar_prerequisitos():
            return False
        total, sucessos, cancelado = processar_todos_videos()

        if cancelado:
            raise KeyboardInterrupt()

        if total == 0:
            return True

        return sucessos > 0
        
    except KeyboardInterrupt:
        try:
            _ = cleanup.limpar_temp_audios()
        except Exception:
            raise
        try:
            _ = cleanup.limpar_pycache()
        except Exception:
            raise
        return True
    except Exception:
        raise
    finally:
        transcriber.limpar_modelo()
        cleanup.limpar_temp_audios()
        cleanup.limpar_pycache()


if __name__ == "__main__":
    try:
        sucesso = False
        try:
            sucesso = main()
        except KeyboardInterrupt:
            pass
        finally:
            print(f"\n✅ Sistema finalizado\n")

        if sucesso:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        transcriber.limpar_modelo()
        cleanup.limpar_temp_audios()
        cleanup.limpar_pycache()
