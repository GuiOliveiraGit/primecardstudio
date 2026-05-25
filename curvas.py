from PIL import Image
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
import os

from banco_cartas import carregar_banco
from config import EXTENSOES_IMAGEM


def exportar_pdf_com_texto_em_curvas(janela_pai=None):

    pasta_imagens = filedialog.askdirectory(
        title="Selecione a pasta das artes sem texto"
    )

    if not pasta_imagens:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione onde salvar os PDFs em curvas"
    )

    if not pasta_saida:
        return

    banco = carregar_banco()

    arquivos = sorted([
        f for f in os.listdir(pasta_imagens)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning(
            "Nenhuma imagem",
            "Nenhuma arte encontrada na pasta."
        )
        return

    total = 0
    ignoradas = 0

    for arquivo in arquivos:

        nome_arquivo, ext = os.path.splitext(arquivo)

        if nome_arquivo not in banco:
            print(f"Sem dados no banco para: {nome_arquivo}")
            ignoradas += 1
            continue

        dados = banco[nome_arquivo]

        nome = dados.get("nome", nome_arquivo.title())
        subtitulo = dados.get("subtitulo", "")
        habilidades = dados.get("habilidades", [])

        caminho_imagem = os.path.join(pasta_imagens, arquivo)
        caminho_pdf = os.path.join(
            pasta_saida,
            f"{nome_arquivo}_curvas.pdf"
        )

        try:
            gerar_pdf_carta_curvas(
                caminho_imagem,
                caminho_pdf,
                nome,
                subtitulo,
                habilidades
            )

            total += 1

        except Exception as e:
            print(f"Erro em {arquivo}: {e}")
            ignoradas += 1

    messagebox.showinfo(
        "PDF com curvas",
        f"PDFs criados com sucesso!\n\n"
        f"Gerados: {total}\n"
        f"Ignorados: {ignoradas}"
    )


def gerar_pdf_carta_curvas(
    caminho_imagem,
    caminho_pdf,
    nome,
    subtitulo,
    habilidades
):

    imagem = Image.open(caminho_imagem).convert("RGB")
    largura, altura = imagem.size

    pdf = canvas.Canvas(
        caminho_pdf,
        pagesize=(largura, altura)
    )

    pdf.drawImage(
        ImageReader(imagem),
        0,
        0,
        width=largura,
        height=altura
    )

    # ============================================================
    # POSIÇÕES PADRÃO
    # Ajustamos depois conforme seu template
    # ============================================================

    nome_y = altura - int(altura * 0.08)
    subtitulo_y = int(altura * 0.355)
    habilidades_y = int(altura * 0.29)

    margem_x = int(largura * 0.08)
    largura_texto = largura - (margem_x * 2)

    # ============================================================
    # NOME
    # ============================================================

    desenhar_texto_curva(
        pdf,
        texto=nome,
        x=largura / 2,
        y=nome_y,
        tamanho=int(altura * 0.032),
        centralizado=True,
        cor=(1, 1, 1),
        negrito=True
    )

    # ============================================================
    # SUBTÍTULO
    # ============================================================

    if subtitulo:

        desenhar_texto_curva(
            pdf,
            texto=subtitulo,
            x=margem_x,
            y=subtitulo_y,
            tamanho=int(altura * 0.024),
            centralizado=False,
            cor=(1, 1, 1),
            negrito=True
        )

    # ============================================================
    # HABILIDADES
    # ============================================================

    y_atual = habilidades_y

    for habilidade in habilidades:

        nome_ataque = habilidade.get("nome", "").strip()
        descricao = habilidade.get("descricao", "").strip()

        if nome_ataque:

            desenhar_texto_curva(
                pdf,
                texto=f"{nome_ataque}:",
                x=margem_x,
                y=y_atual,
                tamanho=int(altura * 0.019),
                centralizado=False,
                cor=(1, 1, 1),
                negrito=True
            )

            y_atual -= int(altura * 0.026)

        if descricao:

            linhas = quebrar_linhas_curvas(
                descricao,
                largura_texto,
                tamanho=int(altura * 0.017)
            )

            for linha in linhas:

                desenhar_texto_curva(
                    pdf,
                    texto=linha,
                    x=margem_x,
                    y=y_atual,
                    tamanho=int(altura * 0.017),
                    centralizado=False,
                    cor=(0.95, 0.95, 0.95),
                    negrito=False
                )

                y_atual -= int(altura * 0.022)

        y_atual -= int(altura * 0.015)

    pdf.save()


def desenhar_texto_curva(
    pdf,
    texto,
    x,
    y,
    tamanho=24,
    centralizado=False,
    cor=(1, 1, 1),
    negrito=False
):

    fonte = FontProperties(
        family="DejaVu Sans",
        weight="bold" if negrito else "regular"
    )

    text_path = TextPath(
        (0, 0),
        texto,
        size=tamanho,
        prop=fonte
    )

    bbox = text_path.get_extents()
    largura_texto = bbox.width

    if centralizado:
        x = x - largura_texto / 2

    pdf.saveState()
    pdf.setFillColorRGB(*cor)

    path_pdf = pdf.beginPath()

    vertices = text_path.vertices
    codes = text_path.codes

    i = 0

    while i < len(vertices):

        codigo = codes[i]
        ponto = vertices[i]

        px = ponto[0] + x
        py = ponto[1] + y

        if codigo == Path.MOVETO:
            path_pdf.moveTo(px, py)

        elif codigo == Path.LINETO:
            path_pdf.lineTo(px, py)

        elif codigo == Path.CURVE3:
            # Curva quadrática convertida de forma simples
            if i + 1 < len(vertices):
                p1 = vertices[i]
                p2 = vertices[i + 1]

                x1 = p1[0] + x
                y1 = p1[1] + y
                x2 = p2[0] + x
                y2 = p2[1] + y

                path_pdf.curveTo(
                    x1,
                    y1,
                    x2,
                    y2,
                    x2,
                    y2
                )

                i += 1

        elif codigo == Path.CURVE4:
            if i + 2 < len(vertices):
                p1 = vertices[i]
                p2 = vertices[i + 1]
                p3 = vertices[i + 2]

                path_pdf.curveTo(
                    p1[0] + x,
                    p1[1] + y,
                    p2[0] + x,
                    p2[1] + y,
                    p3[0] + x,
                    p3[1] + y
                )

                i += 2

        elif codigo == Path.CLOSEPOLY:
            path_pdf.close()

        i += 1

    pdf.drawPath(
        path_pdf,
        stroke=0,
        fill=1
    )

    pdf.restoreState()


def quebrar_linhas_curvas(texto, largura_max, tamanho):

    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:

        teste = linha_atual + (" " if linha_atual else "") + palavra

        if medir_texto_curva(teste, tamanho) <= largura_max:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)

            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas


def medir_texto_curva(texto, tamanho):

    fonte = FontProperties(
        family="DejaVu Sans"
    )

    text_path = TextPath(
        (0, 0),
        texto,
        size=tamanho,
        prop=fonte
    )

    bbox = text_path.get_extents()

    return bbox.width
