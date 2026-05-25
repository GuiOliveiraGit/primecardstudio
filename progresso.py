import tkinter as tk
from tkinter import ttk


class JanelaProgresso:
    def __init__(self, janela_pai, titulo, total):
        self.total = max(total, 1)
        self.janela = tk.Toplevel(janela_pai) if janela_pai else tk.Toplevel()
        self.janela.title(titulo)
        self.janela.geometry("420x130")
        self.janela.resizable(False, False)
        self.janela.grab_set()

        self.texto = tk.StringVar(value="Preparando...")

        tk.Label(
            self.janela,
            textvariable=self.texto,
            font=("Arial", 11)
        ).pack(pady=(18, 8))

        self.barra = ttk.Progressbar(
            self.janela,
            maximum=self.total,
            mode="determinate",
            length=350
        )
        self.barra.pack(pady=6)

        self.contador = tk.StringVar(value=f"0 de {self.total}")

        tk.Label(
            self.janela,
            textvariable=self.contador,
            font=("Arial", 9),
            fg="gray"
        ).pack()

        self.janela.update_idletasks()

    def atualizar(self, atual, texto=None):
        atual = min(max(atual, 0), self.total)
        self.barra["value"] = atual
        self.contador.set(f"{atual} de {self.total}")

        if texto:
            self.texto.set(texto)

        self.janela.update_idletasks()

    def fechar(self):
        self.janela.grab_release()
        self.janela.destroy()
