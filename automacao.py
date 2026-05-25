import csv
import os
from tkinter import filedialog, messagebox

from banco_cartas import salvar_carta


def importar_csv_cartas(janela_pai=None):

    caminho_csv = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=[("CSV", "*.csv")]
    )

    if not caminho_csv:
        return

    total = 0

    try:
        with open(caminho_csv, "r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";")

            for linha in leitor:

                nome_arquivo = linha.get("arquivo", "").strip()

                if not nome_arquivo:
                    continue

                nome_arquivo = os.path.splitext(nome_arquivo)[0]

                habilidades = []

                for i in range(1, 7):
                    nome_ataque = linha.get(f"ataque{i}_nome", "").strip()
                    descricao = linha.get(f"ataque{i}_descricao", "").strip()

                    if nome_ataque or descricao:
                        habilidades.append({
                            "nome": nome_ataque,
                            "descricao": descricao
                        })

                quantidade = linha.get("quantidade", "").strip()

                if quantidade.isdigit():
                    quantidade = int(quantidade)
                else:
                    quantidade = None

                salvar_carta(
                    nome_arquivo=nome_arquivo,
                    nome=linha.get("nome", "").strip(),
                    subtitulo=linha.get("subtitulo", "").strip(),
                    habilidades=habilidades,
                    cor=linha.get("cor", "#FFFFFF").strip(),
                    estilo=linha.get("estilo", "Minimalista").strip(),
                    quantidade=quantidade
                )

                total += 1

        messagebox.showinfo(
            "CSV importado",
            f"{total} carta(s) importada(s) para o banco de dados."
        )

    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Erro ao importar CSV:\n{e}"
        )