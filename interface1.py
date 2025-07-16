import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import sys
import io

# Importa a função principal
from _main import atualizar_dados  # Certifique-se que o nome do arquivo está certo

# Classe para capturar os prints e exibir na interface
class CapturaSaida(io.StringIO):
    def __init__(self, widget_texto):
        super().__init__()
        self.widget_texto = widget_texto

    def write(self, mensagem):
        self.widget_texto.insert(tk.END, mensagem)
        self.widget_texto.see(tk.END)  # rola o texto automaticamente

    def flush(self):
        pass

# Função para rodar a automação em thread (sem travar a interface)
def executar_automacao():
    try:
        atualizar_dados()
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

def iniciar_execucao():
    # Limpa a tela e redireciona o stdout
    texto_saida.delete("1.0", tk.END)
    sys.stdout = CapturaSaida(texto_saida)
    sys.stderr = sys.stdout  # também mostra os erros
    threading.Thread(target=executar_automacao).start()

# Cria a interface
janela = tk.Tk()
janela.title("Atualizador de Comunicação de Ativos")
janela.geometry("700x500")

# Botão de executar
botao = tk.Button(janela, text="▶ Executar", font=("Arial", 12), command=iniciar_execucao)
botao.pack(pady=10)

# Área de exibição dos prints
texto_saida = ScrolledText(janela, wrap=tk.WORD, font=("Courier", 10))
texto_saida.pack(expand=True, fill='both')

# Inicia a janela
janela.mainloop()
