def plural(count: int, singular: str, plural: str = None) -> str:
    """
    Retorna a forma correta (singular/plural) baseada em 'count'.

    Exemplo: plural(1, 'arquivo') -> 'arquivo'
             plural(2, 'arquivo') -> 'arquivos'
    """
    if plural is None:
        plural = singular + "s"
    return singular if count == 1 else plural


def confirmar_acao(pergunta, opcoes_sim=['S', 'SIM'], opcoes_nao=['N', 'NAO', 'NÃO']):
    """
    Exibe uma pergunta no terminal e aguarda resposta Sim/Não do usuário.

    Retorna True para resposta afirmativa e False para negativa.
    Aceita variações como 'S', 'SIM', 'N', 'NAO', 'NÃO' (case-insensitive).
    """
    opcoes_sim = [op.upper() for op in opcoes_sim]
    opcoes_nao = [op.upper() for op in opcoes_nao]
    prompt = f"{pergunta} [S=Sim, N=Não]: "
    while True:
        resposta = input(prompt).strip()
        resposta_upper = resposta.upper()

        if resposta_upper in opcoes_sim:
            return True
        if resposta_upper in opcoes_nao:
            return False

        print(f"   ❌ Digite uma opção válida: 'S' para Sim ou 'N' para Não\n")


def exibir_cabecalho(titulo: str = None, width: int = 60):
    """
    Exibe um cabeçalho simples no terminal para separar seções da saída.
    """
    if not titulo:
        titulo = "📊 SISTEMA DE TRANSCRIÇÃO"

    divisor = '─' * 3
    cab = f"{divisor} {titulo} {divisor}"
    print()
    print(cab)


def formatar_duracao(segundos_total: float) -> str:
    """
    Formata um tempo (em segundos) em uma string legível, por exemplo:
    3661 -> '1 hora, 1 minuto e 1 segundo'
    """
    total = int(segundos_total)
    horas = total // 3600
    minutos = (total % 3600) // 60
    segundos = total % 60
    partes = []
    if horas > 0:
        partes.append(f"{horas} {plural(horas, 'hora')}")
    if minutos > 0:
        partes.append(f"{minutos} {plural(minutos, 'minuto')}")
    if segundos > 0 or not partes:
        partes.append(f"{segundos} {plural(segundos, 'segundo')}")
    if len(partes) == 1:
        return partes[0]
    if len(partes) == 2:
        return f"{partes[0]} e {partes[1]}"
    return f"{partes[0]}, {partes[1]} e {partes[2]}"
