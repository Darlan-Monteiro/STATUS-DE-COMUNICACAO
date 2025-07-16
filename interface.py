import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import sys
import io
from _main import atualizar_dados  # Agora não roda atualizar_dados() na importação

class CapturaSaida(io.StringIO):
    def __init__(self, widget_texto):
        super().__init__()
        self.widget_texto = widget_texto

    def write(self, mensagem):
        self.widget_texto.insert(tk.END, mensagem)
        self.widget_texto.see(tk.END)

    def flush(self):
        pass

def executar_automacao():
    try:
        atualizar_dados()
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

def iniciar_execucao():
    texto_saida.delete("1.0", tk.END)
    sys.stdout = CapturaSaida(texto_saida)
    sys.stderr = sys.stdout
    threading.Thread(target=executar_automacao).start()

janela = tk.Tk()
janela.title("Atualizador de Comunicação de Ativos")
janela.geometry("700x500")

botao = tk.Button(janela, text="▶ Executar", font=("Arial", 12), command=iniciar_execucao)
botao.pack(pady=10)

texto_saida = ScrolledText(janela, wrap=tk.WORD, font=("Courier", 10))
texto_saida.pack(expand=True, fill='both')

janela.mainloop()
