from banco_cartas import obter_carta, salvar_nome
from PIL import Image, ImageDraw, ImageFont
import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from config import EXTENSOES_IMAGEM

# ============================================================
# EXTENSÕES ACEITAS
# ============================================================

# ============================================================
# FUNÇÃO PÚBLICA: CRIAR CAIXA DE NOME ESTILO MAGIC
# Chamada pelo main.py passando a janela principal como pai
# ============================================================

def criar_caixa_nome_magic(janela_pai=None):

    pasta_imagens = filedialog.askdirectory(
        title="Selecione a pasta das cartas"
    )

    if not pasta_imagens:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione a pasta onde salvar"
    )

    if not pasta_saida:
        return

    # ====================================================
    # JANELA DE ESCOLHA DE ESTILO
    # ====================================================

    estilo_escolhido = {"valor": None}

    janela_estilo = tk.Toplevel(janela_pai)
    janela_estilo.title("Escolha o Estilo da Caixa")
    janela_estilo.geometry("420x280")
    janela_estilo.resizable(False, False)
    janela_estilo.grab_set()

    tk.Label(
        janela_estilo,
        text="Escolha o estilo da caixa de nome:",
        font=("Georgia", 13, "bold")
    ).pack(pady=18)

    tk.Label(
        janela_estilo,
        text="🖤  Estilo Dark (ex: Mastermind Plum)\n"
             "Borda colorida, fundo escuro translúcido, letra branca.\n",
        font=("Arial", 10),
        justify="left"
    ).pack(padx=20)

    tk.Label(
        janela_estilo,
        text="✨  Estilo Dourado (ex: Alela, Artful Provocateur)\n"
             "Borda dourada, fundo claro esmaecido, letra escura.\n",
        font=("Arial", 10),
        justify="left"
    ).pack(padx=20)

    def escolher(estilo):
        estilo_escolhido["valor"] = estilo
        janela_estilo.destroy()

    frame_botoes = tk.Frame(janela_estilo)
    frame_botoes.pack(pady=10)

    tk.Button(
        frame_botoes,
        text="🖤 Estilo Dark",
        font=("Arial", 11, "bold"),
        width=16,
        height=2,
        bg="#1a1a2e",
        fg="white",
        command=lambda: escolher("dark")
    ).pack(side="left", padx=10)

    tk.Button(
        frame_botoes,
        text="✨ Estilo Dourado",
        font=("Arial", 11, "bold"),
        width=16,
        height=2,
        bg="#c8a84b",
        fg="#1a0a00",
        command=lambda: escolher("dourado")
    ).pack(side="left", padx=10)

    janela_estilo.wait_window()

    if estilo_escolhido["valor"] is None:
        return

    estilo = estilo_escolhido["valor"]

    # ====================================================
    # PROCESSAR IMAGENS
    # ====================================================

    total = 0

    arquivos_validos = sorted([
        f for f in os.listdir(pasta_imagens)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    total_cartas = len(arquivos_validos)

    for indice, arquivo in enumerate(arquivos_validos, start=1):

        nome_arquivo, ext = os.path.splitext(arquivo)

        nome_personagem = (
            nome_arquivo
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )

        caminho_imagem = os.path.join(pasta_imagens, arquivo)

        # ================================================
        # JANELA DE PREVIEW AO VIVO + ESCOLHA DE COR
        # ================================================

        resposta = _pedir_cor_por_carta(
            janela_pai,
            caminho_imagem,
            nome_personagem,
            estilo,
            indice,
            total_cartas
        )

        # None significa que o usuário pulou esta carta
        if resposta is None:
            print(f"Pulado: {nome_personagem}")
            continue

        # Para estilo dark, resposta é a cor hex escolhida
        # Para estilo dourado, resposta é a string "dourado" (sem cor)
        cor_borda_hex = resposta if estilo == "dark" else None

        try:

            imagem_original = Image.open(caminho_imagem).convert("RGBA")

            # Reutiliza _renderizar_preview para gerar a imagem final
            # (mesma função usada no preview ao vivo — resultado idêntico)
            resultado = _renderizar_preview(
                imagem_original,
                estilo,
                cor_borda_hex,
                nome_personagem
            )

            caminho_saida = os.path.join(
                pasta_saida,
                f"{nome_arquivo}_nome.png"
            )

            resultado.save(caminho_saida)
            total += 1

        except Exception as e:
            print(f"Erro em {arquivo}: {e}")

    messagebox.showinfo(
        "Concluído",
        f"Caixa de nome criada em {total} imagem(ns)."
    )


# ============================================================
# HELPER: RENDERIZA A CARTA COM A CAIXA DE NOME APLICADA
# Retorna um Image PIL pronto para exibir ou salvar
# ============================================================

def _renderizar_preview(imagem_original, estilo, cor_borda_hex, nome_personagem):

    imagem = imagem_original.copy()
    largura, altura = imagem.size

    camada = Image.new("RGBA", imagem.size, (0, 0, 0, 0))
    draw   = ImageDraw.Draw(camada)

    # Medidas base
    margem_x     = int(largura * 0.055)
    topo         = int(altura  * 0.055)
    caixa_altura = int(altura  * 0.075)

    x1 = margem_x
    y1 = topo
    x2 = largura - margem_x
    y2 = topo + caixa_altura

    raio          = int(caixa_altura * 0.30)
    borda         = int(largura * 0.009)
    sombra_offset = int(largura * 0.006)

    # Fonte
    tamanho_fonte = int(caixa_altura * 0.52)

    fontes_possiveis = [
        "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
        "C:/Windows/Fonts/arialbd.ttf"
    ]

    fonte_path_ok = None

    for fp in fontes_possiveis:
        if os.path.exists(fp):
            fonte_path_ok = fp
            break

    def carregar_fonte(tamanho):
        if fonte_path_ok:
            return ImageFont.truetype(fonte_path_ok, tamanho)
        return ImageFont.load_default()

    fonte = carregar_fonte(tamanho_fonte)

    while tamanho_fonte > 20:
        bbox = draw.textbbox((0, 0), nome_personagem, font=fonte)
        if (bbox[2] - bbox[0]) <= (x2 - x1) * 0.82:
            break
        tamanho_fonte -= 2
        fonte = carregar_fonte(tamanho_fonte)

    if estilo == "dark":
        _desenhar_estilo_dark(
            draw, x1, y1, x2, y2, raio, borda,
            sombra_offset, caixa_altura, largura,
            cor_borda_hex, nome_personagem, fonte
        )
    elif estilo == "dourado":
        _desenhar_estilo_dourado(
            draw, x1, y1, x2, y2, raio, borda,
            sombra_offset, caixa_altura, largura,
            nome_personagem, fonte
        )

    return Image.alpha_composite(imagem, camada)


# ============================================================
# HELPER: JANELA DE PREVIEW AO VIVO + SELEÇÃO DE COR POR CARTA
# ============================================================

def _pedir_cor_por_carta(
    janela_pai,
    caminho_imagem,
    nome_personagem,
    estilo,
    indice,
    total_cartas
):
    from PIL import ImageTk

    resultado = {"cor": None}

    # Carrega a imagem original uma vez
    try:
        imagem_original = Image.open(caminho_imagem).convert("RGBA")
        largura_orig, altura_orig = imagem_original.size
    except Exception:
        imagem_original = None
        largura_orig, altura_orig = 200, 280

    PREVIEW_ALTURA  = 340
    proporcao       = largura_orig / altura_orig
    PREVIEW_LARGURA = int(PREVIEW_ALTURA * proporcao)

    janela_cor = tk.Toplevel(janela_pai)
    janela_cor.title(f"Carta {indice} de {total_cartas}  —  {nome_personagem}")
    janela_cor.resizable(False, False)
    janela_cor.grab_set()

    # ====================================================
    # LABEL DA IMAGEM (preview ao vivo)
    # ====================================================

    label_img = tk.Label(janela_cor)
    label_img.pack(padx=16, pady=(16, 4))

    # Referência mantida para evitar garbage collection
    label_img._foto_ref = None

    def atualizar_preview(cor_hex):
        if imagem_original is None:
            return
        try:
            renderizado = _renderizar_preview(
                imagem_original, estilo, cor_hex, nome_personagem
            )
            renderizado = renderizado.resize(
                (PREVIEW_LARGURA, PREVIEW_ALTURA),
                Image.LANCZOS
            )
            foto = ImageTk.PhotoImage(renderizado)
            label_img.config(image=foto)
            label_img._foto_ref = foto   # manter referência
        except Exception as e:
            print(f"Erro ao renderizar preview: {e}")

    # Preview inicial: sem cor (estilo dourado) ou imagem original (dark)
    if estilo == "dourado":
        atualizar_preview(None)
    else:
        # Mostra a carta limpa enquanto nenhuma cor foi escolhida
        try:
            img_limpa = imagem_original.resize(
                (PREVIEW_LARGURA, PREVIEW_ALTURA),
                Image.LANCZOS
            )
            foto_inicial = ImageTk.PhotoImage(img_limpa)
            label_img.config(image=foto_inicial)
            label_img._foto_ref = foto_inicial
        except Exception:
            pass

    # ====================================================
    # NOME E CONTADOR
    # ====================================================

    tk.Label(
        janela_cor,
        text=nome_personagem,
        font=("Georgia", 12, "bold")
    ).pack(pady=(0, 0))

    tk.Label(
        janela_cor,
        text=f"Carta {indice} de {total_cartas}",
        font=("Arial", 9),
        fg="gray"
    ).pack(pady=(0, 8))

    # ====================================================
    # AMOSTRA DE COR + BOTÃO ESCOLHER (só no estilo dark)
    # ====================================================

    if estilo == "dark":

        frame_cor = tk.Frame(janela_cor)
        frame_cor.pack(pady=(0, 4))

        tk.Label(
            frame_cor,
            text="Cor da borda: ",
            font=("Arial", 10)
        ).pack(side="left")

        amostra_cor = tk.Label(
            frame_cor,
            text="   ",
            bg="#444444",
            relief="solid",
            width=4
        )
        amostra_cor.pack(side="left")

        label_hex = tk.Label(
            frame_cor,
            text="nenhuma",
            font=("Arial", 9),
            fg="gray"
        )
        label_hex.pack(side="left", padx=6)

        def abrir_colorchooser():
            cor = colorchooser.askcolor(
                title=f"Cor da borda para {nome_personagem}",
                parent=janela_cor
            )
            if cor[1]:
                resultado["cor"] = cor[1]
                amostra_cor.config(bg=cor[1])
                label_hex.config(text=cor[1])
                atualizar_preview(cor[1])   # ← ATUALIZA O PREVIEW AO VIVO

        tk.Button(
            janela_cor,
            text="🎨 Escolher cor da borda",
            font=("Arial", 10, "bold"),
            width=24,
            height=1,
            command=abrir_colorchooser
        ).pack(pady=(0, 6))

    # ====================================================
    # BOTÕES CONFIRMAR / PULAR
    # ====================================================

    frame_acoes = tk.Frame(janela_cor)
    frame_acoes.pack(pady=(2, 14))

    def confirmar():
        if estilo == "dark" and resultado["cor"] is None:
            from tkinter import messagebox as mb
            mb.showwarning(
                "Atenção",
                "Escolha uma cor antes de confirmar.",
                parent=janela_cor
            )
            return
        # Para estilo dourado, cor não é necessária
        if estilo == "dourado":
            resultado["cor"] = "dourado"
        janela_cor.destroy()

    def pular():
        resultado["cor"] = None
        janela_cor.destroy()

    tk.Button(
        frame_acoes,
        text="✔ Confirmar",
        font=("Arial", 10, "bold"),
        width=14,
        height=1,
        bg="#2a6e2a",
        fg="white",
        command=confirmar
    ).pack(side="left", padx=8)

    tk.Button(
        frame_acoes,
        text="⏭ Pular carta",
        font=("Arial", 10),
        width=14,
        height=1,
        command=pular
    ).pack(side="left", padx=8)

    janela_cor.wait_window()

    # Retorna None se pulou, a cor hex se dark, "dourado" se dourado
    return resultado["cor"]


# ============================================================
# ESTILO DARK (inspirado em Mastermind Plum)
# Borda colorida viva, interior escuro translúcido, letra branca
# ============================================================

def _desenhar_estilo_dark(
    draw, x1, y1, x2, y2, raio, borda,
    sombra_offset, caixa_altura, largura,
    cor_borda_hex, nome_personagem, fonte
):
    # Recuo de 2mm em cada lado
    # Uma carta Magic mede ~63mm de largura → 2mm = largura * (2/63)
    recuo_2mm = int(largura * (2 / 63))
    x1 = x1 + recuo_2mm
    x2 = x2 - recuo_2mm

    # Sombra
    draw.rounded_rectangle(
        [
            x1 + sombra_offset, y1 + sombra_offset,
            x2 + sombra_offset, y2 + sombra_offset
        ],
        radius=raio,
        fill=(0, 0, 0, 160)
    )

    # Borda colorida (cor escolhida pelo usuário)
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=raio,
        fill=cor_borda_hex
    )

    # Interior escuro (quase preto, leve transparência)
    draw.rounded_rectangle(
        [x1 + borda, y1 + borda, x2 - borda, y2 - borda],
        radius=raio,
        fill=(18, 10, 25, 230)
    )

    # Brilho superior sutil (reflexo interno)
    draw.rounded_rectangle(
        [
            x1 + borda * 2,
            y1 + borda * 2,
            x2 - borda * 2,
            y1 + int(caixa_altura * 0.42)
        ],
        radius=raio,
        fill=(255, 255, 255, 28)
    )

    # Filete interno roxo/branco translúcido
    espessura_filete = max(2, int(largura * 0.003))

    draw.rounded_rectangle(
        [x1 + borda, y1 + borda, x2 - borda, y2 - borda],
        radius=raio,
        outline=(200, 180, 255, 140),
        width=espessura_filete
    )

    # Posição do texto — centralizado horizontalmente na caixa
    bbox = draw.textbbox((0, 0), nome_personagem, font=fonte)
    texto_largura = bbox[2] - bbox[0]
    texto_altura  = bbox[3] - bbox[1]

    texto_x = x1 + ((x2 - x1) - texto_largura) // 2
    texto_y = (
        y1
        + ((caixa_altura - texto_altura) // 2)
        - int(caixa_altura * 0.06)
    )

    # Sombra do texto
    draw.text(
        (texto_x + 2, texto_y + 2),
        nome_personagem,
        font=fonte,
        fill=(0, 0, 0, 190)
    )

    # Texto branco principal
    draw.text(
        (texto_x, texto_y),
        nome_personagem,
        font=fonte,
        fill=(255, 255, 255, 255)
    )


# ============================================================
# ESTILO DOURADO (inspirado em Alela, Artful Provocateur)
# Borda dupla dourada, fundo creme translúcido, letra escura
# ============================================================

def _desenhar_estilo_dourado(
    draw, x1, y1, x2, y2, raio, borda,
    sombra_offset, caixa_altura, largura,
    nome_personagem, fonte
):
    # Recuo de 2mm em cada lado
    recuo_2mm = int(largura * (2 / 63))
    x1 = x1 + recuo_2mm
    x2 = x2 - recuo_2mm

    OURO_ESCURO  = (120,  85,  20, 255)
    OURO_MEDIO   = (180, 140,  45, 255)
    OURO_CLARO   = (220, 185,  90, 255)
    OURO_BRILHO  = (255, 230, 140, 200)
    FUNDO_CREME  = (235, 220, 185, 210)
    TEXTO_ESCURO = ( 25,  12,   5, 255)

    # Sombra suave
    draw.rounded_rectangle(
        [
            x1 + sombra_offset, y1 + sombra_offset,
            x2 + sombra_offset, y2 + sombra_offset
        ],
        radius=raio,
        fill=(0, 0, 0, 110)
    )

    # Borda externa escura (moldura mais externa)
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=raio,
        fill=OURO_ESCURO
    )

    # Borda dourada intermediária
    margem1 = int(largura * 0.006)

    draw.rounded_rectangle(
        [
            x1 + margem1, y1 + margem1,
            x2 - margem1, y2 - margem1
        ],
        radius=raio,
        fill=OURO_CLARO
    )

    # Interior creme translúcido
    margem2 = int(largura * 0.012)

    draw.rounded_rectangle(
        [
            x1 + margem2, y1 + margem2,
            x2 - margem2, y2 - margem2
        ],
        radius=raio,
        fill=FUNDO_CREME
    )

    # Brilho superior dourado (reflexo)
    draw.rounded_rectangle(
        [
            x1 + margem2 + 2,
            y1 + margem2 + 2,
            x2 - margem2 - 2,
            y1 + int(caixa_altura * 0.40)
        ],
        radius=raio,
        fill=OURO_BRILHO
    )

    # Filete interno fino (detalhe de luxo)
    espessura_filete = max(2, int(largura * 0.003))

    draw.rounded_rectangle(
        [
            x1 + margem2, y1 + margem2,
            x2 - margem2, y2 - margem2
        ],
        radius=raio,
        outline=OURO_MEDIO,
        width=espessura_filete
    )

    # Posição do texto — centralizado horizontalmente na caixa
    bbox = draw.textbbox((0, 0), nome_personagem, font=fonte)
    texto_largura = bbox[2] - bbox[0]
    texto_altura  = bbox[3] - bbox[1]

    texto_x = x1 + ((x2 - x1) - texto_largura) // 2
    texto_y = (
        y1
        + ((caixa_altura - texto_altura) // 2)
        - int(caixa_altura * 0.06)
    )

    # Sombra suave dourada
    draw.text(
        (texto_x + 1, texto_y + 2),
        nome_personagem,
        font=fonte,
        fill=(150, 110, 30, 160)
    )

    # Texto escuro principal
    draw.text(
        (texto_x, texto_y),
        nome_personagem,
        font=fonte,
        fill=TEXTO_ESCURO
    )
