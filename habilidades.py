from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from presets import obter_preset, listar_presets
from templates import obter_template, listar_templates
from banco_cartas import salvar_habilidades, obter_carta
from config import EXTENSOES_IMAGEM


def adicionar_habilidades(janela_pai=None):

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

    arquivos = sorted([
        f for f in os.listdir(pasta_imagens)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning(
            "Nenhuma imagem",
            "Nenhuma carta encontrada na pasta selecionada."
        )
        return

    total = 0

    for arquivo in arquivos:

        nome_arquivo, ext = os.path.splitext(arquivo)
        caminho_imagem = os.path.join(pasta_imagens, arquivo)

        dados_banco = obter_carta(nome_arquivo)

        subtitulo_padrao = dados_banco.get("subtitulo", "")

        subtitulo = simpledialog.askstring(
            "Subtítulo",
            f"Digite o subtítulo para:\n{nome_arquivo}",
            initialvalue=subtitulo_padrao
        )

        if not subtitulo:
            continue

        habilidades_banco = dados_banco.get("habilidades", [])

        usar_banco = False

        if habilidades_banco:
            usar_banco = messagebox.askyesno(
                "Habilidades salvas",
                f"Já existem habilidades salvas para {nome_arquivo}.\n\n"
                "Deseja usar as habilidades do banco?"
            )

        habilidades = []

        if usar_banco:

            habilidades = habilidades_banco

        else:

            quantidade = simpledialog.askinteger(
                "Ataques / Habilidades",
                f"Quantos ataques ou habilidades {nome_arquivo} terá?",
                minvalue=1,
                maxvalue=6
            )

            if not quantidade:
                continue

            for i in range(quantidade):

                nome_ataque = simpledialog.askstring(
                    "Nome do ataque",
                    f"Digite o nome do ataque/habilidade {i + 1}:"
                )

                if not nome_ataque:
                    nome_ataque = "Habilidade"

                descricao = simpledialog.askstring(
                    "Descrição",
                    f"Digite a descrição de:\n{nome_ataque}"
                )

                if not descricao:
                    descricao = ""

                habilidades.append({
                    "nome": nome_ataque,
                    "descricao": descricao
                })

        config = abrir_editor_visual(
            janela_pai,
            caminho_imagem,
            subtitulo,
            habilidades,
            nome_arquivo
        )

        if config is None:
            continue

        try:
            imagem = Image.open(caminho_imagem).convert("RGBA")

            resultado = desenhar_habilidades(
                imagem,
                subtitulo,
                habilidades,
                config
            )

            caminho_saida = os.path.join(
                pasta_saida,
                f"{nome_arquivo}_habilidades.png"
            )

            resultado.save(caminho_saida)
            total += 1

        except Exception as e:
            print(f"Erro em {arquivo}: {e}")

    messagebox.showinfo(
        "Concluído",
        f"Habilidades adicionadas em {total} carta(s)."
    )


def abrir_editor_visual(
    janela_pai,
    caminho_imagem,
    subtitulo,
    habilidades,
    nome_arquivo
):

    imagem_original = Image.open(caminho_imagem).convert("RGBA")
    largura, altura = imagem_original.size

    dados_banco = obter_carta(nome_arquivo)

    posicoes_banco = dados_banco.get("posicoes", {})
    fontes_banco = dados_banco.get("fontes", {})

    config = {
        "cor": dados_banco.get("cor", "#C30212"),
        "estilo": dados_banco.get("estilo", "sem_borda"),
        "transparencia": 120,
        "sub_y": posicoes_banco.get("sub_y", 0.64),
        "atk_y": posicoes_banco.get("atk_y", 0.715),
        "fonte_sub": fontes_banco.get("fonte_sub", 0.55),
        "fonte_ataque": fontes_banco.get("fonte_ataque", 0.031),
        "fonte_texto": fontes_banco.get("fonte_texto", 0.028),
        "alinhamento": dados_banco.get("alinhamento", "esquerda"),
        "confirmado": False
    }

    janela = tk.Toplevel(janela_pai)
    janela.title(f"Editor de Habilidades — {nome_arquivo}")
    janela.geometry("780x760")
    janela.resizable(False, False)
    janela.grab_set()

    frame_principal = tk.Frame(janela)
    frame_principal.pack(fill="both", expand=True)

    frame_preview = tk.Frame(frame_principal)
    frame_preview.pack(side="left", padx=10, pady=10)

    preview_altura = 620
    preview_largura = int(preview_altura * largura / altura)

    canvas = tk.Canvas(
        frame_preview,
        width=preview_largura,
        height=preview_altura,
        bg="#222222"
    )
    canvas.pack()

    frame_controles = tk.Frame(frame_principal)
    frame_controles.pack(side="right", fill="y", padx=10, pady=10)

    tk.Label(
        frame_controles,
        text="Editor Visual",
        font=("Arial", 15, "bold")
    ).pack(pady=8)

    # ============================================================
    # COR
    # ============================================================

    tk.Label(
        frame_controles,
        text="Cor da borda / separador"
    ).pack(anchor="w")

    entrada_cor = tk.Entry(frame_controles, width=18)
    entrada_cor.insert(0, config["cor"])
    entrada_cor.pack(anchor="w", pady=3)

    entrada_cor.bind("<KeyRelease>", lambda event: atualizar_preview())

    # ============================================================
    # ESTILO
    # ============================================================

    estilo_var = tk.StringVar(value=config["estilo"])

    tk.Label(
        frame_controles,
        text="Estilo da caixa"
    ).pack(anchor="w", pady=(10, 0))

    tk.OptionMenu(
        frame_controles,
        estilo_var,
        "com_borda",
        "borda_fina",
        "sem_borda",
        command=lambda x: atualizar_preview()
    ).pack(anchor="w", pady=3)

    # ============================================================
    # PRESETS
    # ============================================================

    tk.Label(
        frame_controles,
        text="Preset visual"
    ).pack(anchor="w", pady=(10, 0))

    preset_var = tk.StringVar(
        value=dados_banco.get("preset", "Minimalista")
    )

    def aplicar_preset(*args):

        preset = obter_preset(preset_var.get())

        estilo_var.set(preset["estilo"])
        escala_transparencia.set(preset["transparencia"])
        alinhamento_var.set(preset["alinhamento"])

        entrada_cor.delete(0, tk.END)
        entrada_cor.insert(0, preset["cor"])

        atualizar_preview()

    preset_menu = tk.OptionMenu(
        frame_controles,
        preset_var,
        *listar_presets(),
        command=aplicar_preset
    )

    preset_menu.pack(anchor="w", pady=3)

    # ============================================================
    # TEMPLATE
    # ============================================================

    tk.Label(
        frame_controles,
        text="Template"
    ).pack(anchor="w", pady=(10, 0))

    template_var = tk.StringVar(
        value=dados_banco.get("template", "Magic")
    )

    tk.OptionMenu(
        frame_controles,
        template_var,
        *listar_templates(),
        command=lambda x: atualizar_preview()
    ).pack(anchor="w", pady=3)

    # ============================================================
    # TRANSPARÊNCIA
    # ============================================================

    tk.Label(
        frame_controles,
        text="Transparência do fundo"
    ).pack(anchor="w", pady=(10, 0))

    escala_transparencia = tk.Scale(
        frame_controles,
        from_=0,
        to=255,
        orient="horizontal",
        length=220,
        command=lambda x: atualizar_preview()
    )

    escala_transparencia.set(config["transparencia"])
    escala_transparencia.pack(anchor="w")

    # ============================================================
    # POSIÇÕES
    # ============================================================

    tk.Label(
        frame_controles,
        text="Posição do subtítulo"
    ).pack(anchor="w", pady=(10, 0))

    escala_sub_y = tk.Scale(
        frame_controles,
        from_=45,
        to=80,
        orient="horizontal",
        length=220,
        command=lambda x: atualizar_preview()
    )

    escala_sub_y.set(int(config["sub_y"] * 100))
    escala_sub_y.pack(anchor="w")

    tk.Label(
        frame_controles,
        text="Posição dos ataques"
    ).pack(anchor="w", pady=(10, 0))

    escala_atk_y = tk.Scale(
        frame_controles,
        from_=50,
        to=90,
        orient="horizontal",
        length=220,
        command=lambda x: atualizar_preview()
    )

    escala_atk_y.set(int(config["atk_y"] * 100))
    escala_atk_y.pack(anchor="w")

    # ============================================================
    # FONTES
    # ============================================================

    tk.Label(
        frame_controles,
        text="Tamanho fonte subtítulo"
    ).pack(anchor="w", pady=(10, 0))

    escala_fonte_sub = tk.Scale(
        frame_controles,
        from_=35,
        to=80,
        orient="horizontal",
        length=220,
        command=lambda x: atualizar_preview()
    )

    escala_fonte_sub.set(int(config["fonte_sub"] * 100))
    escala_fonte_sub.pack(anchor="w")

    tk.Label(
        frame_controles,
        text="Tamanho fonte ataque"
    ).pack(anchor="w", pady=(10, 0))

    escala_fonte_ataque = tk.Scale(
        frame_controles,
        from_=18,
        to=45,
        orient="horizontal",
        length=220,
        command=lambda x: atualizar_preview()
    )

    escala_fonte_ataque.set(int(config["fonte_ataque"] * 1000))
    escala_fonte_ataque.pack(anchor="w")

    tk.Label(
        frame_controles,
        text="Tamanho fonte descrição"
    ).pack(anchor="w", pady=(10, 0))

    escala_fonte_texto = tk.Scale(
        frame_controles,
        from_=16,
        to=40,
        orient="horizontal",
        length=220,
        command=lambda x: atualizar_preview()
    )

    escala_fonte_texto.set(int(config["fonte_texto"] * 1000))
    escala_fonte_texto.pack(anchor="w")

    # ============================================================
    # ALINHAMENTO
    # ============================================================

    tk.Label(
        frame_controles,
        text="Alinhamento do texto"
    ).pack(anchor="w", pady=(10, 0))

    alinhamento_var = tk.StringVar(value=config["alinhamento"])

    tk.OptionMenu(
        frame_controles,
        alinhamento_var,
        "esquerda",
        "centro",
        command=lambda x: atualizar_preview()
    ).pack(anchor="w", pady=3)

    imagem_preview_ref = {"foto": None}

    def obter_config_atual():

        cor = entrada_cor.get().strip()

        if not cor.startswith("#"):
            cor = "#" + cor

        if len(cor) != 7:
            cor = "#FFFFFF"

        return {
            "cor": cor,
            "estilo": estilo_var.get(),
            "transparencia": escala_transparencia.get(),
            "sub_y": escala_sub_y.get() / 100,
            "atk_y": escala_atk_y.get() / 100,
            "fonte_sub": escala_fonte_sub.get() / 100,
            "fonte_ataque": escala_fonte_ataque.get() / 1000,
            "fonte_texto": escala_fonte_texto.get() / 1000,
            "alinhamento": alinhamento_var.get(),
            "confirmado": False
        }

    def atualizar_preview():

        cfg = obter_config_atual()

        template = obter_template(template_var.get())

        # Para usar depois em ajustes de layout
        _ = template

        render = desenhar_habilidades(
            imagem_original,
            subtitulo,
            habilidades,
            cfg
        )

        render = render.resize(
            (preview_largura, preview_altura),
            Image.LANCZOS
        )

        foto = ImageTk.PhotoImage(render)

        canvas.delete("all")
        canvas.create_image(
            0,
            0,
            anchor="nw",
            image=foto
        )

        imagem_preview_ref["foto"] = foto

        canvas.create_text(
            10,
            10,
            anchor="nw",
            fill="white",
            text="Dica: arraste subtítulo ou ataques para mover verticalmente.",
            font=("Arial", 9, "bold")
        )

    # ============================================================
    # ARRASTAR COM MOUSE
    # ============================================================

    drag = {"tipo": None}

    def identificar_area(event):

        y_real = event.y / preview_altura

        sub_y = escala_sub_y.get() / 100
        atk_y = escala_atk_y.get() / 100

        if abs(y_real - sub_y) < 0.06:
            return "subtitulo"

        if abs(y_real - atk_y) < 0.15:
            return "ataque"

        return None

    def iniciar_drag(event):
        drag["tipo"] = identificar_area(event)

    def mover_drag(event):

        if drag["tipo"] is None:
            return

        novo_y = int((event.y / preview_altura) * 100)

        if drag["tipo"] == "subtitulo":
            novo_y = max(45, min(80, novo_y))
            escala_sub_y.set(novo_y)

        elif drag["tipo"] == "ataque":
            novo_y = max(50, min(90, novo_y))
            escala_atk_y.set(novo_y)

        atualizar_preview()

    def finalizar_drag(event):
        drag["tipo"] = None

    canvas.bind("<ButtonPress-1>", iniciar_drag)
    canvas.bind("<B1-Motion>", mover_drag)
    canvas.bind("<ButtonRelease-1>", finalizar_drag)

    # ============================================================
    # BOTÕES
    # ============================================================

    frame_botoes = tk.Frame(frame_controles)
    frame_botoes.pack(pady=18)

    def confirmar():

        cfg = obter_config_atual()

        salvar_habilidades(
            nome_arquivo=nome_arquivo,
            subtitulo=subtitulo,
            habilidades=habilidades,
            cor=cfg["cor"],
            estilo=cfg["estilo"],
            preset=preset_var.get(),
            template=template_var.get(),
            posicoes={
                "sub_y": cfg["sub_y"],
                "atk_y": cfg["atk_y"]
            },
            fontes={
                "fonte_sub": cfg["fonte_sub"],
                "fonte_ataque": cfg["fonte_ataque"],
                "fonte_texto": cfg["fonte_texto"]
            }
        )

        cfg["confirmado"] = True

        config.update(cfg)

        janela.destroy()

    def cancelar():
        janela.destroy()

    tk.Button(
        frame_botoes,
        text="Atualizar Preview",
        width=18,
        command=atualizar_preview
    ).pack(pady=4)

    tk.Button(
        frame_botoes,
        text="Confirmar",
        width=18,
        bg="#2a6e2a",
        fg="white",
        command=confirmar
    ).pack(pady=4)

    tk.Button(
        frame_botoes,
        text="Cancelar",
        width=18,
        command=cancelar
    ).pack(pady=4)

    atualizar_preview()

    janela.wait_window()

    if config["confirmado"]:
        return config

    return None


def desenhar_habilidades(
    imagem,
    subtitulo,
    habilidades,
    config
):

    largura, altura = imagem.size

    cor_borda = config["cor"]
    estilo_caixa = config["estilo"]
    transparencia_fundo = config["transparencia"]
    alinhamento = config["alinhamento"]

    camada = Image.new(
        "RGBA",
        imagem.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(camada)

    margem_lateral = int(largura * 0.055)
    margem_inferior = int(altura * 0.055)

    caixa_sub_y = int(altura * config["sub_y"])
    caixa_sub_altura = int(altura * 0.065)

    caixa_texto_y = int(altura * config["atk_y"])
    caixa_texto_max_y = altura - margem_inferior

    x1 = margem_lateral
    x2 = largura - margem_lateral

    recuo_1mm = int(largura * (1 / 63))

    x1_ataque = x1 + recuo_1mm
    x2_ataque = x2 - recuo_1mm

    raio = int(caixa_sub_altura * 0.28)
    borda = max(2, int(largura * 0.006))

    fonte_titulo = carregar_fonte(
        "bold",
        int(caixa_sub_altura * config["fonte_sub"])
    )

    fonte_ataque = carregar_fonte(
        "bold",
        int(altura * config["fonte_ataque"])
    )

    fonte_texto = carregar_fonte(
        "regular",
        int(altura * config["fonte_texto"])
    )

    # ============================================================
    # SUBTÍTULO
    # ============================================================

    desenhar_caixa(
        draw,
        x1,
        caixa_sub_y,
        x2,
        caixa_sub_y + caixa_sub_altura,
        raio,
        borda,
        cor_borda,
        estilo_caixa,
        transparencia_fundo
    )

    bbox = draw.textbbox(
        (0, 0),
        subtitulo,
        font=fonte_titulo
    )

    texto_largura = bbox[2] - bbox[0]
    texto_altura = bbox[3] - bbox[1]

    if alinhamento == "centro":
        subtitulo_x = x1 + ((x2 - x1) - texto_largura) // 2
    else:
        subtitulo_x = x1 + int(largura * 0.035)

    subtitulo_y = (
        caixa_sub_y
        + ((caixa_sub_altura - texto_altura) // 2)
        - int(caixa_sub_altura * 0.08)
    )

    draw.text(
        (subtitulo_x + 2, subtitulo_y + 2),
        subtitulo,
        font=fonte_titulo,
        fill=(0, 0, 0, 200)
    )

    draw.text(
        (subtitulo_x, subtitulo_y),
        subtitulo,
        font=fonte_titulo,
        fill=(255, 255, 255, 255)
    )

    # ============================================================
    # ATAQUES
    # ============================================================

    raio_texto = int(caixa_sub_altura * 0.24)

    desenhar_caixa(
        draw,
        x1_ataque,
        caixa_texto_y,
        x2_ataque,
        caixa_texto_max_y,
        raio_texto,
        borda,
        cor_borda,
        estilo_caixa,
        transparencia_fundo
    )

    padding_x = int(largura * 0.045)
    padding_y = int(altura * 0.018)

    texto_x = x1_ataque + padding_x
    texto_y = caixa_texto_y + padding_y

    largura_texto = (
        (x2_ataque - x1_ataque)
        - (padding_x * 2)
    )

    linhas = montar_linhas(
        draw,
        habilidades,
        fonte_ataque,
        fonte_texto,
        largura_texto
    )

    desenhar_linhas(
        draw,
        linhas,
        texto_x,
        texto_y,
        x1_ataque,
        x2_ataque,
        fonte_ataque,
        fonte_texto,
        cor_borda,
        altura,
        caixa_texto_max_y - padding_y,
        alinhamento,
        largura_texto
    )

    return Image.alpha_composite(
        imagem,
        camada
    )


def desenhar_caixa(
    draw,
    x1,
    y1,
    x2,
    y2,
    raio,
    borda,
    cor_borda,
    estilo,
    transparencia
):

    if estilo == "sem_borda":

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=raio,
            fill=(0, 0, 0, transparencia)
        )

    elif estilo == "borda_fina":

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=raio,
            fill=(0, 0, 0, transparencia),
            outline=cor_borda,
            width=2
        )

    else:

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=raio,
            fill=cor_borda
        )

        draw.rounded_rectangle(
            [
                x1 + borda,
                y1 + borda,
                x2 - borda,
                y2 - borda
            ],
            radius=raio,
            fill=(0, 0, 0, transparencia)
        )


def montar_linhas(
    draw,
    habilidades,
    fonte_ataque,
    fonte_texto,
    largura_texto
):

    linhas = []

    for idx, habilidade in enumerate(habilidades):

        nome = habilidade.get("nome", "").strip()
        descricao = habilidade.get("descricao", "").strip()

        if nome:
            linhas.append({
                "tipo": "ataque",
                "texto": f"{nome}:"
            })

        palavras = descricao.split()
        linha_atual = ""

        for palavra in palavras:

            teste = linha_atual + (
                " " if linha_atual else ""
            ) + palavra

            bbox = draw.textbbox(
                (0, 0),
                teste,
                font=fonte_texto
            )

            teste_largura = bbox[2] - bbox[0]

            if teste_largura <= largura_texto:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append({
                        "tipo": "descricao",
                        "texto": linha_atual
                    })

                linha_atual = palavra

        if linha_atual:
            linhas.append({
                "tipo": "descricao",
                "texto": linha_atual
            })

        if idx < len(habilidades) - 1:
            linhas.append({
                "tipo": "separador",
                "texto": ""
            })

    return linhas


def desenhar_linhas(
    draw,
    linhas,
    texto_x,
    texto_y,
    x1,
    x2,
    fonte_ataque,
    fonte_texto,
    cor_borda,
    altura,
    limite_y,
    alinhamento,
    largura_texto
):

    y = texto_y

    espaco_linha = int(altura * 0.009)
    espaco_ataque = int(altura * 0.008)
    espaco_separador = int(altura * 0.020)

    for linha in linhas:

        if y > limite_y:
            break

        tipo = linha["tipo"]

        if tipo in ["ataque", "descricao"]:

            fonte = fonte_ataque if tipo == "ataque" else fonte_texto
            texto = linha["texto"]

            bbox = draw.textbbox(
                (0, 0),
                texto,
                font=fonte
            )

            texto_largura = bbox[2] - bbox[0]
            texto_altura = bbox[3] - bbox[1]

            if y + texto_altura > limite_y:
                break

            if alinhamento == "centro":
                x = texto_x + (
                    (largura_texto - texto_largura) // 2
                )
            else:
                x = texto_x

            fill_principal = (
                (255, 255, 255, 255)
                if tipo == "ataque"
                else (245, 245, 245, 255)
            )

            draw.text(
                (x + 2, y + 2),
                texto,
                font=fonte,
                fill=(0, 0, 0, 200)
            )

            draw.text(
                (x, y),
                texto,
                font=fonte,
                fill=fill_principal
            )

            if tipo == "ataque":
                y += texto_altura + espaco_ataque
            else:
                y += texto_altura + espaco_linha

        elif tipo == "separador":

            y += int(espaco_separador * 0.35)

            if y > limite_y:
                break

            draw.line(
                [
                    (texto_x, y),
                    (
                        x2 - int((x2 - x1) * 0.045),
                        y
                    )
                ],
                fill=cor_borda,
                width=max(2, int(altura * 0.002))
            )

            y += int(espaco_separador * 0.65)


def carregar_fonte(tipo, tamanho):

    tamanho = max(10, int(tamanho))

    if tipo == "bold":

        fontes = [
            "C:/Windows/Fonts/georgiab.ttf",
            "C:/Windows/Fonts/timesbd.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        ]

    else:

        fontes = [
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]

    for fonte in fontes:

        if os.path.exists(fonte):
            return ImageFont.truetype(
                fonte,
                tamanho
            )

    return ImageFont.load_default()
