from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import messagebox
import os


def mostrar_preview_pdf(
    janela_pai,
    frentes,
    versos,
    largura_mm,
    altura_mm,
    sangria_mm,
    margem_segura_mm,
    espacamento_mm,
    mostrar_pontilhado=True,
    mostrar_margem_segura=True,
    mostrar_marcas=True,
    espelhar_verso=True
):

    if not frentes:
        messagebox.showwarning(
            "Preview",
            "Nenhuma carta para pré-visualizar."
        )
        return True

    resultado = {"confirmado": False}
    modo = {"valor": "frente"}

    # A4 em mm
    a4_largura_mm = 210
    a4_altura_mm = 297

    escala = 3  # pixels por mm no preview

    largura_a4_px = int(a4_largura_mm * escala)
    altura_a4_px = int(a4_altura_mm * escala)

    janela = tk.Toplevel(janela_pai)
    janela.title("Preview do PDF")
    janela.geometry("760x940")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Preview da folha A4",
        font=("Arial", 16, "bold")
    ).pack(pady=(12, 4))

    info = tk.Label(
        janela,
        text="Visualizando frente",
        font=("Arial", 10),
        fg="gray"
    )
    info.pack(pady=(0, 8))

    canvas = tk.Canvas(
        janela,
        width=largura_a4_px,
        height=altura_a4_px,
        bg="#333333",
        highlightthickness=0
    )
    canvas.pack(pady=8)

    foto_ref = {"foto": None}

    def gerar_preview(tipo="frente"):

        folha = Image.new(
            "RGB",
            (largura_a4_px, altura_a4_px),
            "white"
        )

        draw = ImageDraw.Draw(folha)

        largura_carta_px = int(largura_mm * escala)
        altura_carta_px = int(altura_mm * escala)
        sangria_px = int(sangria_mm * escala)
        margem_segura_px = int(margem_segura_mm * escala)
        espacamento_px = int(espacamento_mm * escala)

        largura_total_px = largura_carta_px + sangria_px * 2
        altura_total_px = altura_carta_px + sangria_px * 2

        margem_pagina_px = int(10 * escala)

        colunas = int(
            (largura_a4_px - margem_pagina_px * 2 + espacamento_px)
            // (largura_total_px + espacamento_px)
        )

        linhas = int(
            (altura_a4_px - margem_pagina_px * 2 + espacamento_px)
            // (altura_total_px + espacamento_px)
        )

        if colunas < 1 or linhas < 1:
            return folha

        cartas_por_pagina = colunas * linhas

        if tipo == "frente":
            imagens = frentes[:cartas_por_pagina]
        else:
            imagens = versos[:cartas_por_pagina] if versos else []

        largura_grade = (
            colunas * largura_total_px
            + (colunas - 1) * espacamento_px
        )

        altura_grade = (
            linhas * altura_total_px
            + (linhas - 1) * espacamento_px
        )

        inicio_x = int((largura_a4_px - largura_grade) / 2)
        inicio_y = int((altura_a4_px - altura_grade) / 2)

        indice = 0

        for linha in range(linhas):

            for coluna in range(colunas):

                if indice >= len(imagens):
                    return folha

                if tipo == "verso" and espelhar_verso:
                    coluna_real = colunas - 1 - coluna
                else:
                    coluna_real = coluna

                x_total = inicio_x + coluna_real * (
                    largura_total_px + espacamento_px
                )

                y_total = inicio_y + linha * (
                    altura_total_px + espacamento_px
                )

                caminho = imagens[indice]

                try:
                    img = Image.open(caminho).convert("RGB")
                    img = img.resize(
                        (largura_total_px, altura_total_px),
                        Image.LANCZOS
                    )
                    folha.paste(img, (x_total, y_total))
                except Exception:
                    draw.rectangle(
                        [
                            x_total,
                            y_total,
                            x_total + largura_total_px,
                            y_total + altura_total_px
                        ],
                        fill="#dddddd",
                        outline="red"
                    )

                    draw.text(
                        (x_total + 8, y_total + 8),
                        "Erro imagem",
                        fill="red"
                    )

                x_corte = x_total + sangria_px
                y_corte = y_total + sangria_px

                # Pontilhado de corte
                if mostrar_pontilhado:
                    desenhar_retangulo_pontilhado(
                        draw,
                        x_corte,
                        y_corte,
                        largura_carta_px,
                        altura_carta_px,
                        cor="black"
                    )

                # Margem segura
                if mostrar_margem_segura and margem_segura_px > 0:
                    desenhar_retangulo_pontilhado(
                        draw,
                        x_corte + margem_segura_px,
                        y_corte + margem_segura_px,
                        largura_carta_px - margem_segura_px * 2,
                        altura_carta_px - margem_segura_px * 2,
                        cor="#0088ff"
                    )

                # Marcas de corte
                if mostrar_marcas:
                    desenhar_marcas_corte_preview(
                        draw,
                        x_corte,
                        y_corte,
                        largura_carta_px,
                        altura_carta_px
                    )

                indice += 1

        return folha

    def atualizar():

        folha = gerar_preview(modo["valor"])

        foto = ImageTk.PhotoImage(folha)

        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=foto)
        foto_ref["foto"] = foto

        if modo["valor"] == "frente":
            info.config(text="Visualizando frente")
        else:
            info.config(text="Visualizando verso")

    def alternar():

        if modo["valor"] == "frente":
            modo["valor"] = "verso"
        else:
            modo["valor"] = "frente"

        atualizar()

    def confirmar():

        resultado["confirmado"] = True
        janela.destroy()

    def cancelar():

        resultado["confirmado"] = False
        janela.destroy()

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)

    if versos:
        tk.Button(
            frame_botoes,
            text="Alternar Frente / Verso",
            width=22,
            command=alternar
        ).pack(side="left", padx=6)

    tk.Button(
        frame_botoes,
        text="Confirmar e Gerar PDF",
        width=22,
        bg="#2a6e2a",
        fg="white",
        command=confirmar
    ).pack(side="left", padx=6)

    tk.Button(
        frame_botoes,
        text="Cancelar",
        width=14,
        command=cancelar
    ).pack(side="left", padx=6)

    atualizar()

    janela.wait_window()

    return resultado["confirmado"]


def desenhar_retangulo_pontilhado(draw, x, y, largura, altura, cor="black"):

    passo = 8
    traco = 4

    # Topo e baixo
    for i in range(0, largura, passo):
        draw.line(
            [(x + i, y), (min(x + i + traco, x + largura), y)],
            fill=cor,
            width=1
        )
        draw.line(
            [
                (x + i, y + altura),
                (min(x + i + traco, x + largura), y + altura)
            ],
            fill=cor,
            width=1
        )

    # Laterais
    for i in range(0, altura, passo):
        draw.line(
            [(x, y + i), (x, min(y + i + traco, y + altura))],
            fill=cor,
            width=1
        )
        draw.line(
            [
                (x + largura, y + i),
                (x + largura, min(y + i + traco, y + altura))
            ],
            fill=cor,
            width=1
        )


def desenhar_marcas_corte_preview(draw, x, y, largura, altura):

    tamanho = 18
    recuo = 5
    cor = "black"

    # Inferior esquerdo
    draw.line([(x - tamanho, y), (x - recuo, y)], fill=cor, width=1)
    draw.line([(x, y - tamanho), (x, y - recuo)], fill=cor, width=1)

    # Inferior direito
    draw.line(
        [(x + largura + recuo, y), (x + largura + tamanho, y)],
        fill=cor,
        width=1
    )
    draw.line(
        [(x + largura, y - tamanho), (x + largura, y - recuo)],
        fill=cor,
        width=1
    )

    # Superior esquerdo
    draw.line(
        [(x - tamanho, y + altura), (x - recuo, y + altura)],
        fill=cor,
        width=1
    )
    draw.line(
        [(x, y + altura + recuo), (x, y + altura + tamanho)],
        fill=cor,
        width=1
    )

    # Superior direito
    draw.line(
        [
            (x + largura + recuo, y + altura),
            (x + largura + tamanho, y + altura)
        ],
        fill=cor,
        width=1
    )
    draw.line(
        [
            (x + largura, y + altura + recuo),
            (x + largura, y + altura + tamanho)
        ],
        fill=cor,
        width=1
    )