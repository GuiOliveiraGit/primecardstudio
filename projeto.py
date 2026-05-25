import tkinter as tk
from tkinter import filedialog, messagebox

from preferencias import carregar_preferencias, atualizar_preferencias


CAMPOS_PROJETO = [
    ("Nome do projeto", "projeto_nome"),
    ("Pasta de frentes", "pasta_frentes"),
    ("Pasta de versos", "pasta_versos"),
    ("Pasta de saida", "pasta_saida")
]


def abrir_gerenciador_projeto(janela_pai=None):
    preferencias = carregar_preferencias()
    janela = tk.Toplevel(janela_pai)
    janela.title("Projeto")
    janela.geometry("620x330")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Gerenciador de projeto",
        font=("Arial", 15, "bold")
    ).pack(pady=(18, 12))

    corpo = tk.Frame(janela)
    corpo.pack(fill="both", expand=True, padx=20)

    entradas = {}

    for linha, (rotulo, chave) in enumerate(CAMPOS_PROJETO):
        tk.Label(corpo, text=rotulo).grid(
            row=linha,
            column=0,
            sticky="w",
            pady=6
        )

        entrada = tk.Entry(corpo, width=58)
        entrada.insert(0, preferencias.get(chave, ""))
        entrada.grid(row=linha, column=1, sticky="ew", pady=6, padx=(8, 4))
        entradas[chave] = entrada

        if chave != "projeto_nome":
            tk.Button(
                corpo,
                text="...",
                width=4,
                command=lambda c=chave: escolher_pasta(entradas[c])
            ).grid(row=linha, column=2, pady=6)

    corpo.columnconfigure(1, weight=1)

    def salvar():
        valores = {
            chave: entrada.get().strip()
            for chave, entrada in entradas.items()
        }

        atualizar_preferencias(**valores)
        messagebox.showinfo("Projeto", "Projeto salvo nas preferencias.")
        janela.destroy()

    tk.Button(
        janela,
        text="Salvar projeto",
        width=22,
        command=salvar
    ).pack(pady=16)


def escolher_pasta(entrada):
    pasta = filedialog.askdirectory(title="Selecione a pasta")

    if pasta:
        entrada.delete(0, "end")
        entrada.insert(0, pasta)
