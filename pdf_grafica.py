from preview_pdf import mostrar_preview_pdf
from banco_cartas import salvar_carta
from config import EXTENSOES_IMAGEM, PRESETS_CARTA, TIPOS_ARQUIVO_IMAGEM
from preferencias import atualizar_preferencias, obter_preferencia
from PIL import Image
import os
import math
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

def gerar_pdf_grafica(janela_pai=None):

    pasta_frentes = filedialog.askdirectory(
        title="Selecione a pasta das frentes"
    )
    if not pasta_frentes:
        return

    modo_pdf = pedir_opcao(
        janela_pai,
        "Modo de PDF",
        "Escolha o modo de exportação:",
        [
            "Frente e verso automático",
            "Páginas separadas por tipo",
            "Exportar só frentes",
            "Exportar só versos"
        ]
    )

    if not modo_pdf:
        return

    caminho_verso_unico = None
    pasta_versos = None

    if modo_pdf != "Exportar só frentes":

        tipo_verso = pedir_opcao(
            janela_pai,
            "Tipo de verso",
            "Escolha o tipo de verso:",
            [
                "Verso único para todas",
                "Múltiplos versos por nome do arquivo"
            ]
        )

        if not tipo_verso:
            return

        if tipo_verso == "Verso único para todas":

            caminho_verso_unico = filedialog.askopenfilename(
                title="Selecione o verso das cartas",
                filetypes=TIPOS_ARQUIVO_IMAGEM
            )

            if not caminho_verso_unico:
                return

        else:

            pasta_versos = filedialog.askdirectory(
                title="Selecione a pasta dos versos"
            )

            if not pasta_versos:
                return

    caminho_pdf = filedialog.asksaveasfilename(
        title="Salvar PDF como",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not caminho_pdf:
        return

    preset = escolher_preset_carta(janela_pai)

    if not preset:
        return

    largura_mm = simpledialog.askfloat(
        "Largura",
        "Digite a largura final da carta em mm:",
        minvalue=1,
        initialvalue=preset["largura_mm"]
    )

    if not largura_mm:
        return

    altura_mm = simpledialog.askfloat(
        "Altura",
        "Digite a altura final da carta em mm:",
        minvalue=1,
        initialvalue=preset["altura_mm"]
    )

    if not altura_mm:
        return

    quantidade = simpledialog.askinteger(
        "Quantidade",
        "Quantas cópias de cada carta deseja imprimir?",
        minvalue=1,
        initialvalue=obter_preferencia("quantidade_pdf", 2)
    )

    if not quantidade:
        return
    

    espacamento_mm = simpledialog.askfloat(
        "Espaçamento",
        "Espaçamento entre cartas em mm:",
        minvalue=0,
        initialvalue=preset["espacamento_mm"]
    )

    if espacamento_mm is None:
        return

    sangria_mm = simpledialog.askfloat(
        "Sangria",
        "Digite a sangria em mm, no máximo 3 mm:",
        minvalue=0,
        maxvalue=3,
        initialvalue=preset["sangria_mm"]
    )

    if sangria_mm is None:
        return

    sangria_mm = min(sangria_mm, 3)

    mostrar_margem_segura = messagebox.askyesno(
        "Margem segura",
        "Deseja mostrar margem segura?"
    )

    margem_segura_mm = 0

    if mostrar_margem_segura:

        margem_segura_mm = simpledialog.askfloat(
            "Margem segura",
            "Digite a margem segura em mm:",
            minvalue=0,
            maxvalue=20,
            initialvalue=preset["margem_segura_mm"]
        )

        if margem_segura_mm is None:
            return

    mostrar_pontilhado = messagebox.askyesno(
        "Pontilhado",
        "Deseja mostrar pontilhado de corte?"
    )

    mostrar_marcas = messagebox.askyesno(
        "Marcas de corte",
        "Deseja mostrar marcas de corte profissionais?"
    )

    espelhar_verso = False
    ajuste_x_verso_mm = 0
    ajuste_y_verso_mm = 0

    if modo_pdf != "Exportar só frentes":

        espelhar_verso = messagebox.askyesno(
            "Alinhamento do verso",
            "Deseja espelhar o verso horizontalmente?\n\n"
            "Normalmente use SIM para impressão frente e verso virando na borda longa."
        )

        ajuste_x_verso_mm = simpledialog.askfloat(
            "Alinhamento fino do verso",
            "Deslocamento horizontal do verso em mm:\n"
            "Use negativo para esquerda e positivo para direita.\n\n"
            "Exemplo: 0",
            initialvalue=0
        )

        if ajuste_x_verso_mm is None:
            return

        ajuste_y_verso_mm = simpledialog.askfloat(
            "Alinhamento fino do verso",
            "Deslocamento vertical do verso em mm:\n"
            "Use negativo para baixo e positivo para cima.\n\n"
            "Exemplo: 0",
            initialvalue=0
        )

        if ajuste_y_verso_mm is None:
            return

    arquivos_frente = sorted([
        f for f in os.listdir(pasta_frentes)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos_frente:
        messagebox.showwarning(
            "Nenhuma carta",
            "Nenhuma frente foi encontrada."
        )
        return

    lista_frentes = []
    lista_versos = []

    for arquivo in arquivos_frente:
        nome_arquivo, ext = os.path.splitext(arquivo)

        salvar_carta(
            nome_arquivo=nome_arquivo,
            quantidade=quantidade
        )

        caminho_frente = os.path.join(pasta_frentes, arquivo)

        caminho_verso = None

        if modo_pdf != "Exportar só frentes":

            if caminho_verso_unico:
                caminho_verso = caminho_verso_unico
            else:
                caminho_verso = encontrar_verso_correspondente(
                    pasta_versos,
                    arquivo
                )

                if caminho_verso is None:
                    messagebox.showwarning(
                        "Verso não encontrado",
                        f"Não encontrei verso correspondente para:\n{arquivo}\n\n"
                        "Essa carta será ignorada."
                    )
                    continue

        for _ in range(quantidade):
            lista_frentes.append(caminho_frente)

            if modo_pdf != "Exportar só frentes":
                lista_versos.append(caminho_verso)

    if modo_pdf == "Exportar só versos":
        lista_frentes = []

    if modo_pdf == "Exportar só frentes":
        lista_versos = []

    if not lista_frentes and not lista_versos:
        messagebox.showwarning(
            "Nada para exportar",
            "Nenhuma carta foi selecionada para o PDF."
        )
        return

    mm = 72 / 25.4

    largura_carta = largura_mm * mm
    altura_carta = altura_mm * mm
    sangria = sangria_mm * mm
    margem_segura = margem_segura_mm * mm
    espacamento = espacamento_mm * mm

    ajuste_x_verso = ajuste_x_verso_mm * mm
    ajuste_y_verso = ajuste_y_verso_mm * mm

    largura_total = largura_carta + sangria * 2
    altura_total = altura_carta + sangria * 2

    largura_pagina, altura_pagina = A4
    margem_pagina = 10 * mm

    colunas = int(
        (largura_pagina - margem_pagina * 2 + espacamento)
        // (largura_total + espacamento)
    )

    linhas = int(
        (altura_pagina - margem_pagina * 2 + espacamento)
        // (altura_total + espacamento)
    )

    if colunas < 1 or linhas < 1:
        messagebox.showerror(
            "Erro",
            "As cartas estão grandes demais para caber na folha A4."
        )
        return

    cartas_por_pagina = colunas * linhas
    
    confirmar_preview = mostrar_preview_pdf(
        janela_pai=janela_pai,
        frentes=lista_frentes,
        versos=lista_versos,
        largura_mm=largura_mm,
        altura_mm=altura_mm,
        sangria_mm=sangria_mm,
        margem_segura_mm=margem_segura_mm,
        espacamento_mm=espacamento_mm,
        mostrar_pontilhado=mostrar_pontilhado,
        mostrar_margem_segura=mostrar_margem_segura,
        mostrar_marcas=mostrar_marcas,
        espelhar_verso=espelhar_verso
    )

    if not confirmar_preview:
        return

    pdf = canvas.Canvas(caminho_pdf, pagesize=A4)

    if modo_pdf == "Frente e verso automático":

        gerar_frente_verso_intercalado(
            pdf,
            lista_frentes,
            lista_versos,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            cartas_por_pagina,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            espelhar_verso,
            ajuste_x_verso,
            ajuste_y_verso
        )

    elif modo_pdf == "Páginas separadas por tipo":

        gerar_paginas_separadas(
            pdf,
            lista_frentes,
            lista_versos,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            cartas_por_pagina,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            espelhar_verso,
            ajuste_x_verso,
            ajuste_y_verso
        )

    elif modo_pdf == "Exportar só frentes":

        gerar_apenas_um_tipo(
            pdf,
            lista_frentes,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            cartas_por_pagina,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            verso=False,
            espelhar_verso=False,
            ajuste_x_verso=0,
            ajuste_y_verso=0
        )

    elif modo_pdf == "Exportar só versos":

        gerar_apenas_um_tipo(
            pdf,
            lista_versos,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            cartas_por_pagina,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            verso=True,
            espelhar_verso=espelhar_verso,
            ajuste_x_verso=ajuste_x_verso,
            ajuste_y_verso=ajuste_y_verso
        )

    pdf.save()

    atualizar_preferencias(
        preset_pdf=preset["nome"],
        largura_mm=largura_mm,
        altura_mm=altura_mm,
        quantidade_pdf=quantidade,
        espacamento_mm=espacamento_mm,
        sangria_mm=sangria_mm,
        margem_segura_mm=margem_segura_mm
    )

    messagebox.showinfo(
        "PDF criado",
        f"PDF criado com sucesso!\n\n"
        f"Modo: {modo_pdf}\n"
        f"Cartas por página: {cartas_por_pagina}\n"
        f"Arquivo:\n{caminho_pdf}"
    )


def pedir_opcao(janela_pai, titulo, texto, opcoes):

    resultado = {"valor": None}

    janela = tk.Toplevel(janela_pai)
    janela.title(titulo)
    janela.geometry("380x260")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text=texto,
        font=("Arial", 12, "bold")
    ).pack(pady=15)

    for opcao in opcoes:

        tk.Button(
            janela,
            text=opcao,
            width=32,
            height=2,
            command=lambda o=opcao: escolher_opcao(janela, resultado, o)
        ).pack(pady=4)

    janela.wait_window()

    return resultado["valor"]


def escolher_opcao(janela, resultado, valor):

    resultado["valor"] = valor
    janela.destroy()


def escolher_preset_carta(janela_pai):
    opcoes = list(PRESETS_CARTA.keys())
    padrao = obter_preferencia("preset_pdf", opcoes[0])

    if padrao in opcoes:
        opcoes.remove(padrao)
        opcoes.insert(0, padrao)

    escolha = pedir_opcao(
        janela_pai,
        "Tamanho da carta",
        "Escolha um tamanho base:",
        opcoes
    )

    if not escolha:
        return None

    preset = PRESETS_CARTA[escolha].copy()
    preset["nome"] = escolha

    if escolha == "Personalizado":
        preset["largura_mm"] = obter_preferencia(
            "largura_mm",
            preset["largura_mm"]
        )
        preset["altura_mm"] = obter_preferencia(
            "altura_mm",
            preset["altura_mm"]
        )
        preset["sangria_mm"] = obter_preferencia(
            "sangria_mm",
            preset["sangria_mm"]
        )
        preset["margem_segura_mm"] = obter_preferencia(
            "margem_segura_mm",
            preset["margem_segura_mm"]
        )
        preset["espacamento_mm"] = obter_preferencia(
            "espacamento_mm",
            preset["espacamento_mm"]
        )

    return preset


def encontrar_verso_correspondente(pasta_versos, arquivo_frente):

    nome, ext = os.path.splitext(arquivo_frente)

    for extensao in EXTENSOES_IMAGEM:

        tentativa = os.path.join(
            pasta_versos,
            nome + extensao
        )

        if os.path.exists(tentativa):
            return tentativa

    return None


def gerar_frente_verso_intercalado(
    pdf,
    lista_frentes,
    lista_versos,
    largura_pagina,
    altura_pagina,
    largura_carta,
    altura_carta,
    largura_total,
    altura_total,
    sangria,
    margem_segura,
    espacamento,
    colunas,
    linhas,
    cartas_por_pagina,
    mostrar_pontilhado,
    mostrar_marcas,
    mostrar_margem_segura,
    espelhar_verso,
    ajuste_x_verso,
    ajuste_y_verso
):

    total_paginas = math.ceil(len(lista_frentes) / cartas_por_pagina)

    indice = 0

    for _ in range(total_paginas):

        frentes_pagina = lista_frentes[indice: indice + cartas_por_pagina]
        versos_pagina = lista_versos[indice: indice + cartas_por_pagina]

        desenhar_pagina(
            pdf,
            frentes_pagina,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            verso=False,
            espelhar_verso=False,
            ajuste_x_verso=0,
            ajuste_y_verso=0
        )

        pdf.showPage()

        desenhar_pagina(
            pdf,
            versos_pagina,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            verso=True,
            espelhar_verso=espelhar_verso,
            ajuste_x_verso=ajuste_x_verso,
            ajuste_y_verso=ajuste_y_verso
        )

        pdf.showPage()

        indice += cartas_por_pagina


def gerar_paginas_separadas(
    pdf,
    lista_frentes,
    lista_versos,
    largura_pagina,
    altura_pagina,
    largura_carta,
    altura_carta,
    largura_total,
    altura_total,
    sangria,
    margem_segura,
    espacamento,
    colunas,
    linhas,
    cartas_por_pagina,
    mostrar_pontilhado,
    mostrar_marcas,
    mostrar_margem_segura,
    espelhar_verso,
    ajuste_x_verso,
    ajuste_y_verso
):

    gerar_apenas_um_tipo(
        pdf,
        lista_frentes,
        largura_pagina,
        altura_pagina,
        largura_carta,
        altura_carta,
        largura_total,
        altura_total,
        sangria,
        margem_segura,
        espacamento,
        colunas,
        linhas,
        cartas_por_pagina,
        mostrar_pontilhado,
        mostrar_marcas,
        mostrar_margem_segura,
        verso=False,
        espelhar_verso=False,
        ajuste_x_verso=0,
        ajuste_y_verso=0
    )

    gerar_apenas_um_tipo(
        pdf,
        lista_versos,
        largura_pagina,
        altura_pagina,
        largura_carta,
        altura_carta,
        largura_total,
        altura_total,
        sangria,
        margem_segura,
        espacamento,
        colunas,
        linhas,
        cartas_por_pagina,
        mostrar_pontilhado,
        mostrar_marcas,
        mostrar_margem_segura,
        verso=True,
        espelhar_verso=espelhar_verso,
        ajuste_x_verso=ajuste_x_verso,
        ajuste_y_verso=ajuste_y_verso
    )


def gerar_apenas_um_tipo(
    pdf,
    imagens,
    largura_pagina,
    altura_pagina,
    largura_carta,
    altura_carta,
    largura_total,
    altura_total,
    sangria,
    margem_segura,
    espacamento,
    colunas,
    linhas,
    cartas_por_pagina,
    mostrar_pontilhado,
    mostrar_marcas,
    mostrar_margem_segura,
    verso=False,
    espelhar_verso=False,
    ajuste_x_verso=0,
    ajuste_y_verso=0
):

    total_paginas = math.ceil(len(imagens) / cartas_por_pagina)

    indice = 0

    for _ in range(total_paginas):

        imagens_pagina = imagens[indice: indice + cartas_por_pagina]

        desenhar_pagina(
            pdf,
            imagens_pagina,
            largura_pagina,
            altura_pagina,
            largura_carta,
            altura_carta,
            largura_total,
            altura_total,
            sangria,
            margem_segura,
            espacamento,
            colunas,
            linhas,
            mostrar_pontilhado,
            mostrar_marcas,
            mostrar_margem_segura,
            verso=verso,
            espelhar_verso=espelhar_verso,
            ajuste_x_verso=ajuste_x_verso,
            ajuste_y_verso=ajuste_y_verso
        )

        pdf.showPage()

        indice += cartas_por_pagina


def desenhar_pagina(
    pdf,
    imagens,
    largura_pagina,
    altura_pagina,
    largura_carta,
    altura_carta,
    largura_total,
    altura_total,
    sangria,
    margem_segura,
    espacamento,
    colunas,
    linhas,
    mostrar_pontilhado,
    mostrar_marcas,
    mostrar_margem_segura,
    verso=False,
    espelhar_verso=False,
    ajuste_x_verso=0,
    ajuste_y_verso=0
):

    largura_grade = colunas * largura_total + (colunas - 1) * espacamento
    altura_grade = linhas * altura_total + (linhas - 1) * espacamento

    inicio_x = (largura_pagina - largura_grade) / 2
    inicio_y = (altura_pagina - altura_grade) / 2

    indice = 0

    for linha in range(linhas):

        for coluna in range(colunas):

            if indice >= len(imagens):
                return

            if verso and espelhar_verso:
                coluna_real = colunas - 1 - coluna
            else:
                coluna_real = coluna

            x_total = inicio_x + coluna_real * (largura_total + espacamento)

            y_total = (
                altura_pagina
                - inicio_y
                - (linha + 1) * altura_total
                - linha * espacamento
            )

            if verso:
                x_total += ajuste_x_verso
                y_total += ajuste_y_verso

            inserir_imagem_pdf(
                pdf,
                imagens[indice],
                x_total,
                y_total,
                largura_total,
                altura_total
            )

            x_corte = x_total + sangria
            y_corte = y_total + sangria

            if mostrar_pontilhado:

                pdf.saveState()
                pdf.setStrokeColorRGB(0, 0, 0)
                pdf.setLineWidth(0.5)
                pdf.setDash(2, 2)

                pdf.rect(
                    x_corte,
                    y_corte,
                    largura_carta,
                    altura_carta,
                    stroke=1,
                    fill=0
                )

                pdf.restoreState()

            if mostrar_margem_segura:

                pdf.saveState()
                pdf.setStrokeColorRGB(0, 0.5, 1)
                pdf.setLineWidth(0.4)
                pdf.setDash(1, 2)

                pdf.rect(
                    x_corte + margem_segura,
                    y_corte + margem_segura,
                    largura_carta - margem_segura * 2,
                    altura_carta - margem_segura * 2,
                    stroke=1,
                    fill=0
                )

                pdf.restoreState()

            if mostrar_marcas:

                desenhar_marcas_corte(
                    pdf,
                    x_corte,
                    y_corte,
                    largura_carta,
                    altura_carta
                )

            indice += 1


def inserir_imagem_pdf(pdf, caminho_imagem, x, y, largura, altura):

    img = Image.open(caminho_imagem).convert("RGB")

    pdf.drawImage(
        ImageReader(img),
        x,
        y,
        width=largura,
        height=altura,
        preserveAspectRatio=False,
        mask="auto"
    )


def desenhar_marcas_corte(pdf, x, y, largura, altura):

    tamanho = 8

    pdf.saveState()
    pdf.setLineWidth(0.7)
    pdf.setStrokeColorRGB(0, 0, 0)

    # Inferior esquerdo
    pdf.line(x - tamanho, y, x - 2, y)
    pdf.line(x, y - tamanho, x, y - 2)

    # Inferior direito
    pdf.line(x + largura + 2, y, x + largura + tamanho, y)
    pdf.line(x + largura, y - tamanho, x + largura, y - 2)

    # Superior esquerdo
    pdf.line(x - tamanho, y + altura, x - 2, y + altura)
    pdf.line(x, y + altura + 2, x, y + altura + tamanho)

    # Superior direito
    pdf.line(x + largura + 2, y + altura, x + largura + tamanho, y + altura)
    pdf.line(x + largura, y + altura + 2, x + largura, y + altura + tamanho)

    pdf.restoreState()
