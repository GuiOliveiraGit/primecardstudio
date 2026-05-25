import importlib.metadata
import platform
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


PACOTES = {
    "Pillow": "PIL",
    "reportlab": "reportlab",
    "matplotlib": "matplotlib",
    "tkinterdnd2": "tkinterdnd2",
    "pyinstaller": "PyInstaller"
}


def verificar_ambiente(janela_pai=None):
    linhas = [
        "VALIDACAO DO AMBIENTE",
        "=" * 55,
        f"Python: {sys.version.split()[0]}",
        f"Sistema: {platform.system()} {platform.release()}",
        ""
    ]

    for pacote, modulo in PACOTES.items():
        try:
            versao = importlib.metadata.version(pacote)
            linhas.append(f"OK - {pacote}: {versao}")
        except importlib.metadata.PackageNotFoundError:
            linhas.append(f"FALTA - {pacote}")

    linhas.extend([
        "",
        "Para instalar dependencias:",
        "python -m pip install -r requirements.txt",
        "",
        "Para preparar empacotamento:",
        "python -m pip install -r requirements-dev.txt"
    ])

    abrir_relatorio(janela_pai, "\n".join(linhas))


def abrir_relatorio(janela_pai, texto):
    janela = tk.Toplevel(janela_pai)
    janela.title("Validacao do Ambiente")
    janela.geometry("680x520")

    caixa_texto = tk.Text(janela, wrap="word", font=("Consolas", 10))
    caixa_texto.pack(fill="both", expand=True, padx=10, pady=10)
    caixa_texto.insert("1.0", texto)
    caixa_texto.config(state="disabled")

    def salvar():
        caminho = filedialog.asksaveasfilename(
            title="Salvar relatorio",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")]
        )

        if not caminho:
            return

        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)

        messagebox.showinfo("Relatorio salvo", "Relatorio salvo com sucesso.")

    tk.Button(janela, text="Salvar relatorio", command=salvar).pack(pady=8)
