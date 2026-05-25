from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from banco_cartas import carregar_banco, normalizar_chave, nome_exibicao_padrao
from config import EXTENSOES_IMAGEM, TIPOS_ARQUIVO_IMAGEM
from progresso import JanelaProgresso


FONTES_REGISTRADAS = set()


def registrar_fontes():
    fontes = {
        "Beleren": "fonts/beleren.ttf",
        "Arial": "C:/Windows/Fonts/arial.ttf",
        "ArialBold": "C:/Windows/Fonts/arialbd.ttf"
    }

    for nome, caminho in fontes.items():
        if not os.path.exists(caminho):
            continue

        try:
            pdfmetrics.registerFont(TTFont(nome, caminho))
            FONTES_REGISTRADAS.add(nome)
        except Exception:
            pass


def fonte_disponivel(preferida, fallback="Helvetica"):
    if preferida in FONTES_REGISTRADAS:
        return preferida

    return fallback


def exportar_pdf_vetorial(janela_pai=None):
    registrar_fontes()

    modo = pedir_opcao(
        janela_pai,
        "PDF Vetorial",
        "Escolha o modo de exportacao:",
        [
            "Uma carta",
            "Pasta inteira"
        ]
    )

    if not modo:
        return

    if modo == "Uma carta":
        exportar_uma_carta(janela_pai)
    else:
        exportar_pasta(janela_pai)


def exportar_uma_carta(janela_pai=None):
    imagem_path = filedialog.askopenfilename(
        title="Selecione a carta",
        filetypes=TIPOS_ARQUIVO_IMAGEM
    )

    if not imagem_path:
        return

    salvar_pdf = filedialog.asksaveasfilename(
        title="Salvar PDF Vetorial",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not salvar_pdf:
        return

    banco = carregar_banco()
    dados = obter_dados_carta(banco, imagem_path)

    try:
        gerar_pdf_carta_vetorial(imagem_path, salvar_pdf, dados)
    except Exception as erro:
        messagebox.showerror(
            "PDF Vetorial",
            f"Nao foi possivel exportar o PDF:\n{erro}"
        )
        return

    messagebox.showinfo(
        "PDF Vetorial",
        "PDF vetorial exportado com sucesso."
    )


def exportar_pasta(janela_pai=None):
    pasta_imagens = filedialog.askdirectory(
        title="Selecione a pasta das cartas"
    )

    if not pasta_imagens:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione onde salvar os PDFs vetoriais"
    )

    if not pasta_saida:
        return

    arquivos = sorted([
        arquivo for arquivo in os.listdir(pasta_imagens)
        if os.path.splitext(arquivo)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning(
            "PDF Vetorial",
            "Nenhuma imagem encontrada na pasta selecionada."
        )
        return

    banco = carregar_banco()
    total = 0
    erros = []
    progresso = JanelaProgresso(janela_pai, "PDF Vetorial", len(arquivos))

    for indice, arquivo in enumerate(arquivos, start=1):
        progresso.atualizar(indice, f"Exportando {arquivo}")

        caminho_imagem = os.path.join(pasta_imagens, arquivo)
        nome_base = os.path.splitext(arquivo)[0]
        caminho_pdf = os.path.join(pasta_saida, f"{nome_base}_vetorial.pdf")
        dados = obter_dados_carta(banco, caminho_imagem)

        try:
            gerar_pdf_carta_vetorial(caminho_imagem, caminho_pdf, dados)
            total += 1
        except Exception as erro:
            erros.append(f"{arquivo}: {erro}")

    progresso.fechar()
    mostrar_resumo_lote(total, erros)


def obter_dados_carta(banco, caminho_imagem):
    nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
    chave = normalizar_chave(nome_base)

    dados = banco.get(chave)

    if dados is None:
        dados = buscar_carta_por_chave_antiga(banco, chave)

    if dados is None:
        return {
            "nome": nome_exibicao_padrao(nome_base),
            "subtitulo": "",
            "habilidades": []
        }

    return {
        "nome": dados.get("nome") or nome_exibicao_padrao(nome_base),
        "subtitulo": dados.get("subtitulo", ""),
        "habilidades": dados.get("habilidades", [])
    }


def buscar_carta_por_chave_antiga(banco, chave_normalizada):
    for chave, dados in banco.items():
        if normalizar_texto_chave(chave) == normalizar_texto_chave(chave_normalizada):
            return dados

    return None


def normalizar_texto_chave(texto):
    return (
        str(texto)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def gerar_pdf_carta_vetorial(caminho_imagem, caminho_pdf, dados):
    imagem = Image.open(caminho_imagem).convert("RGB")
    largura, altura = imagem.size

    pdf = canvas.Canvas(caminho_pdf, pagesize=(largura, altura))

    pdf.drawImage(
        ImageReader(imagem),
        0,
        0,
        width=largura,
        height=altura
    )

    margem_x = largura * 0.08
    largura_texto = largura - margem_x * 2

    nome = dados.get("nome", "")
    subtitulo = dados.get("subtitulo", "")
    habilidades = dados.get("habilidades", [])

    desenhar_nome(pdf, nome, largura, altura)
    desenhar_subtitulo(pdf, subtitulo, margem_x, altura)
    desenhar_habilidades(pdf, habilidades, margem_x, largura_texto, altura)

    pdf.save()


def desenhar_nome(pdf, nome, largura, altura):
    if not nome:
        return

    tamanho = max(18, int(altura * 0.035))
    fonte = fonte_disponivel("Beleren", "Helvetica-Bold")

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont(fonte, tamanho)
    pdf.drawCentredString(
        largura / 2,
        altura - altura * 0.08,
        ajustar_texto_largura(pdf, nome, fonte, tamanho, largura * 0.84)
    )


def desenhar_subtitulo(pdf, subtitulo, margem_x, altura):
    if not subtitulo:
        return

    tamanho = max(14, int(altura * 0.024))
    fonte = fonte_disponivel("ArialBold", "Helvetica-Bold")

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont(fonte, tamanho)
    pdf.drawString(margem_x, altura * 0.355, subtitulo)


def desenhar_habilidades(pdf, habilidades, margem_x, largura_texto, altura):
    if not habilidades:
        return

    fonte_titulo = fonte_disponivel("ArialBold", "Helvetica-Bold")
    fonte_texto = fonte_disponivel("Arial", "Helvetica")
    tamanho_titulo = max(12, int(altura * 0.019))
    tamanho_texto = max(11, int(altura * 0.016))
    y_atual = altura * 0.29

    for habilidade in habilidades:
        nome = habilidade.get("nome", "").strip()
        descricao = habilidade.get("descricao", "").strip()

        if nome:
            pdf.setFillColorRGB(1, 1, 1)
            pdf.setFont(fonte_titulo, tamanho_titulo)
            pdf.drawString(margem_x, y_atual, f"{nome}:")
            y_atual -= altura * 0.026

        if descricao:
            pdf.setFillColorRGB(0.95, 0.95, 0.95)
            pdf.setFont(fonte_texto, tamanho_texto)

            linhas = quebrar_linhas_pdf(
                descricao,
                fonte_texto,
                tamanho_texto,
                largura_texto
            )

            for linha in linhas:
                pdf.drawString(margem_x, y_atual, linha)
                y_atual -= altura * 0.021

        y_atual -= altura * 0.014


def quebrar_linhas_pdf(texto, fonte, tamanho, largura_maxima):
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        candidata = palavra if not linha_atual else f"{linha_atual} {palavra}"

        if pdfmetrics.stringWidth(candidata, fonte, tamanho) <= largura_maxima:
            linha_atual = candidata
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas


def ajustar_texto_largura(pdf, texto, fonte, tamanho, largura_maxima):
    if pdfmetrics.stringWidth(texto, fonte, tamanho) <= largura_maxima:
        return texto

    sufixo = "..."
    texto_cortado = texto

    while texto_cortado:
        candidato = texto_cortado.rstrip() + sufixo

        if pdfmetrics.stringWidth(candidato, fonte, tamanho) <= largura_maxima:
            return candidato

        texto_cortado = texto_cortado[:-1]

    return sufixo


def pedir_opcao(janela_pai, titulo, texto, opcoes):
    resultado = {"valor": None}

    janela = tk.Toplevel(janela_pai)
    janela.title(titulo)
    janela.geometry("360x220")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text=texto,
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    def escolher(valor):
        resultado["valor"] = valor
        janela.destroy()

    for opcao in opcoes:
        tk.Button(
            janela,
            text=opcao,
            width=28,
            height=2,
            command=lambda valor=opcao: escolher(valor)
        ).pack(pady=5)

    janela.wait_window()
    return resultado["valor"]


def mostrar_resumo_lote(total, erros):
    detalhes = ""

    if erros:
        detalhes = "\n\nOcorrencias:\n" + "\n".join(erros[:12])

        if len(erros) > 12:
            detalhes += f"\n... e mais {len(erros) - 12} ocorrencia(s)."

    messagebox.showinfo(
        "PDF Vetorial",
        f"PDFs gerados: {total}\n"
        f"Erros: {len(erros)}"
        f"{detalhes}"
    )
