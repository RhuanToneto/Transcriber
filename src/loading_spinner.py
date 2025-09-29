import sys
import time
import threading


class SpinnerCarregamento:
    """
    Pequeno utilitário para mostrar um spinner/indicador de progresso
    em linha de comando enquanto uma operação demorada está em execução.

    Uso simples:
      spinner = SpinnerCarregamento("Mensagem...")
      spinner.start()
      ... operação demorada ...
      spinner.stop()
    """
    def __init__(self, mensagem):
        self.mensagem = mensagem
        # Sequência de caracteres usados para criar o efeito de spinner
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧"
        self.running = False
        self.thread = None

    def _spin(self):
        # Função executada em thread separada que atualiza a tela
        i = 0
        while self.running:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            sys.stdout.write(f"\r{char} {self.mensagem}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def start(self):
        # Inicia a thread do spinner
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        # Para o spinner e limpa a linha no terminal
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write(f"\r{' ' * (len(self.mensagem) + 10)}\r")
        sys.stdout.flush()
