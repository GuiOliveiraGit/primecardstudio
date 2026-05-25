from PIL import Image
import os
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from config import EXTENSOES_IMAGEM
from progresso import JanelaProgresso


def exportar_profissional(janela_pai=None):
    pasta_origem = filedialog.askdirectory(
        title="Selecione a pasta das imagens"
    )

    if not pasta_origem:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione onde salvar os arquivos exportados"
    )

    if not pasta_saida:
        return

    formato = escolher_formato(janela_pai)

    if not formato:
        return

    arquivos = sorted([
        f for f in os.listdir(pasta_origem)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning("Nenhuma imagem", "Nenhuma imagem encontrada.")
        return

    if formato == "PDF/X":
        messagebox.showinfo(
            "PDF/X",
            "PDF/X real sera uma etapa futura.\n\n"
            "Por enquanto, use a exportacao PDF normal."
        )
        return

    total = 0
    erros = []
    progresso = JanelaProgresso(janela_pai, "Exportacao", len(arquivos))

    for indice, arquivo in enumerate(arquivos, start=1):
        progresso.atualizar(indice, f"Exportando {arquivo}")

        caminho = os.path.join(pasta_origem, arquivo)
        nome, ext = os.path.splitext(arquivo)

        try:
            imagem = Image.open(caminho).convert("RGBA")

            if formato == "PNG":
                salvar_png(imagem, pasta_saida, nome)
            elif formato == "TIFF":
                salvar_tiff(imagem, pasta_saida, nome)
            elif formato == "PDF":
                salvar_pdf(imagem, pasta_saida, nome)
            elif formato == "SVG":
                salvar_svg_simples(imagem, pasta_saida, nome)

            total += 1

        except Exception as erro:
            erros.append(f"Erro em {arquivo}: {erro}")

    progresso.fechar()
    mostrar_resumo_exportacao(total, formato, erros)


def escolher_formato(janela_pai=None):
    import tkinter as tk

    resultado = {"valor": None}

    janela = tk.Toplevel(janela_pai)
    janela.title("Exportacao Profissional")
    janela.geometry("340x360")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Escolha o formato:",
        font=("Arial", 14, "bold")
    ).pack(pady=18)

    formatos = ["PNG", "PDF", "TIFF", "SVG", "PDF/X"]

    def escolher(valor):
        resultado["valor"] = valor
        janela.destroy()

    for formato in formatos:
        tk.Button(
            janela,
            text=formato,
            width=24,
            height=2,
            command=lambda f=formato: escolher(f)
        ).pack(pady=5)

    janela.wait_window()
    return resultado["valor"]


def salvar_png(imagem, pasta_saida, nome):
    caminho_saida = os.path.join(pasta_saida, f"{nome}.png")
    imagem.save(caminho_saida, format="PNG", dpi=(300, 300))


def salvar_tiff(imagem, pasta_saida, nome):
    caminho_saida = os.path.join(pasta_saida, f"{nome}.tiff")

    imagem.convert("RGB").save(
        caminho_saida,
        format="TIFF",
        compression="tiff_lzw",
        dpi=(300, 300)
    )


def salvar_pdf(imagem, pasta_saida, nome):
    caminho_saida = os.path.join(pasta_saida, f"{nome}.pdf")
    largura_px, altura_px = imagem.size

    pdf = canvas.Canvas(caminho_saida, pagesize=(largura_px, altura_px))
    pdf.drawImage(
        ImageReader(imagem.convert("RGB")),
        0,
        0,
        width=largura_px,
        height=altura_px
    )
    pdf.save()


def salvar_svg_simples(imagem, pasta_saida, nome):
    caminho_png = os.path.join(pasta_saida, f"{nome}_svg_base.png")
    caminho_svg = os.path.join(pasta_saida, f"{nome}.svg")

    imagem.save(caminho_png, format="PNG")
    largura, altura = imagem.size
    nome_png = os.path.basename(caminho_png)

    conteudo_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">
  <image href="{nome_png}" width="{largura}" height="{altura}" />
</svg>
'''

    with open(caminho_svg, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo_svg)


def mostrar_resumo_exportacao(total, formato, erros):
    detalhes = ""

    if erros:
        detalhes = "\n\nOcorrencias:\n" + "\n".join(erros[:12])

        if len(erros) > 12:
            detalhes += f"\n... e mais {len(erros) - 12} ocorrencia(s)."

    messagebox.showinfo(
        "Exportacao concluida",
        f"{total} arquivo(s) exportado(s) em {formato}.\n"
        f"Erros: {len(erros)}"
        f"{detalhes}"
    )
