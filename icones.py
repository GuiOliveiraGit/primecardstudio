from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from config import EXTENSOES_IMAGEM
from progresso import JanelaProgresso


def adicionar_icones(janela_pai=None):
    pasta_personagens = filedialog.askdirectory(
        title="Selecione a pasta das imagens"
    )

    if not pasta_personagens:
        return

    pasta_icones = filedialog.askdirectory(
        title="Selecione a pasta dos icones"
    )

    if not pasta_icones:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione a pasta onde salvar"
    )

    if not pasta_saida:
        return

    arquivos = listar_imagens(pasta_personagens)

    if not arquivos:
        messagebox.showwarning("Nenhuma imagem", "Nenhuma imagem encontrada.")
        return

    amostra = encontrar_primeira_amostra(
        pasta_personagens,
        pasta_icones,
        arquivos
    )

    if amostra is None:
        messagebox.showwarning(
            "Icones",
            "Nenhum icone correspondente foi encontrado.\n\n"
            "Os icones precisam ter o mesmo nome das cartas."
        )
        return

    config = abrir_editor_icones(janela_pai, amostra)

    if not config:
        return

    processar_icones(
        janela_pai,
        pasta_personagens,
        pasta_icones,
        pasta_saida,
        arquivos,
        config
    )


def listar_imagens(pasta):
    return sorted([
        arquivo for arquivo in os.listdir(pasta)
        if os.path.splitext(arquivo)[1].lower() in EXTENSOES_IMAGEM
    ])


def encontrar_primeira_amostra(pasta_personagens, pasta_icones, arquivos):
    for arquivo in arquivos:
        nome, ext = os.path.splitext(arquivo)
        caminho_icone = encontrar_icone(pasta_icones, nome)

        if caminho_icone:
            return {
                "carta": os.path.join(pasta_personagens, arquivo),
                "icone": caminho_icone,
                "nome": nome
            }

    return None


def abrir_editor_icones(janela_pai, amostra):
    config = {
        "tamanho_percentual": 18,
        "pos_x_percentual": 82,
        "pos_y_percentual": 4,
        "confirmado": False
    }

    janela = tk.Toplevel(janela_pai)
    janela.title("Posicionar icone")
    janela.geometry("900x680")
    janela.resizable(False, False)
    janela.grab_set()

    frame_preview = tk.Frame(janela)
    frame_preview.pack(side="left", padx=12, pady=12)

    frame_controles = tk.Frame(janela)
    frame_controles.pack(side="right", fill="y", padx=12, pady=12)

    canvas_largura = 520
    canvas_altura = 620

    canvas = tk.Canvas(
        frame_preview,
        width=canvas_largura,
        height=canvas_altura,
        bg="#222222",
        highlightthickness=0
    )
    canvas.pack()

    foto_ref = {"foto": None}

    tk.Label(
        frame_controles,
        text="Ajuste do icone",
        font=("Arial", 15, "bold")
    ).pack(anchor="w", pady=(4, 14))

    tamanho_var = tk.IntVar(value=config["tamanho_percentual"])
    pos_x_var = tk.IntVar(value=config["pos_x_percentual"])
    pos_y_var = tk.IntVar(value=config["pos_y_percentual"])

    criar_slider(
        frame_controles,
        "Tamanho (% da largura)",
        tamanho_var,
        5,
        45,
        lambda valor: atualizar_preview()
    )

    criar_slider(
        frame_controles,
        "Posicao horizontal (%)",
        pos_x_var,
        0,
        100,
        lambda valor: atualizar_preview()
    )

    criar_slider(
        frame_controles,
        "Posicao vertical (%)",
        pos_y_var,
        0,
        100,
        lambda valor: atualizar_preview()
    )

    tk.Label(
        frame_controles,
        text=(
            "0% horizontal fica na esquerda.\n"
            "100% horizontal fica na direita.\n"
            "0% vertical fica no topo."
        ),
        justify="left",
        fg="gray"
    ).pack(anchor="w", pady=12)

    def atualizar_preview():
        config["tamanho_percentual"] = tamanho_var.get()
        config["pos_x_percentual"] = pos_x_var.get()
        config["pos_y_percentual"] = pos_y_var.get()

        preview = gerar_preview(
            amostra["carta"],
            amostra["icone"],
            config,
            canvas_largura,
            canvas_altura
        )

        foto = ImageTk.PhotoImage(preview)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=foto)
        foto_ref["foto"] = foto

    def confirmar():
        config["confirmado"] = True
        janela.destroy()

    def cancelar():
        janela.destroy()

    tk.Button(
        frame_controles,
        text="Aplicar em todas",
        width=22,
        command=confirmar
    ).pack(anchor="w", pady=(18, 6))

    tk.Button(
        frame_controles,
        text="Cancelar",
        width=22,
        command=cancelar
    ).pack(anchor="w")

    atualizar_preview()
    janela.wait_window()

    if not config["confirmado"]:
        return None

    return config


def criar_slider(parent, texto, variavel, minimo, maximo, comando):
    tk.Label(parent, text=texto).pack(anchor="w", pady=(8, 0))

    escala = tk.Scale(
        parent,
        from_=minimo,
        to=maximo,
        orient="horizontal",
        variable=variavel,
        command=comando,
        length=260
    )
    escala.pack(anchor="w")


def gerar_preview(caminho_carta, caminho_icone, config, largura_max, altura_max):
    carta = Image.open(caminho_carta).convert("RGBA")
    icone = Image.open(caminho_icone).convert("RGBA")
    carta_com_icone = aplicar_icone(carta, icone, config)

    largura, altura = carta_com_icone.size
    escala = min(largura_max / largura, altura_max / altura)
    nova_largura = max(1, int(largura * escala))
    nova_altura = max(1, int(altura * escala))

    preview = Image.new("RGB", (largura_max, altura_max), "#222222")
    carta_redimensionada = carta_com_icone.resize(
        (nova_largura, nova_altura),
        Image.LANCZOS
    ).convert("RGB")

    x = int((largura_max - nova_largura) / 2)
    y = int((altura_max - nova_altura) / 2)
    preview.paste(carta_redimensionada, (x, y))

    return preview


def processar_icones(
    janela_pai,
    pasta_personagens,
    pasta_icones,
    pasta_saida,
    arquivos,
    config
):
    total_processadas = 0
    erros = []
    progresso = JanelaProgresso(janela_pai, "Adicionar icones", len(arquivos))

    for indice, arquivo_personagem in enumerate(arquivos, start=1):
        progresso.atualizar(indice, f"Processando {arquivo_personagem}")

        nome, ext = os.path.splitext(arquivo_personagem)
        caminho_personagem = os.path.join(pasta_personagens, arquivo_personagem)
        caminho_icone = encontrar_icone(pasta_icones, nome)

        if caminho_icone is None:
            erros.append(f"Icone nao encontrado para: {nome}")
            continue

        try:
            personagem = Image.open(caminho_personagem).convert("RGBA")
            icone = Image.open(caminho_icone).convert("RGBA")
            resultado = aplicar_icone(personagem, icone, config)

            caminho_saida = os.path.join(pasta_saida, f"{nome}.png")
            resultado.save(caminho_saida)
            total_processadas += 1

        except Exception as erro:
            erros.append(f"Erro em {nome}: {erro}")

    progresso.fechar()
    mostrar_resumo(total_processadas, erros)


def aplicar_icone(personagem, icone, config):
    largura_personagem, altura_personagem = personagem.size
    tamanho_percentual = config["tamanho_percentual"] / 100
    nova_largura_icone = max(1, int(largura_personagem * tamanho_percentual))
    proporcao = icone.height / icone.width
    nova_altura_icone = max(1, int(nova_largura_icone * proporcao))

    icone = icone.resize(
        (nova_largura_icone, nova_altura_icone),
        Image.LANCZOS
    )

    pos_x = calcular_posicao(
        largura_personagem,
        nova_largura_icone,
        config["pos_x_percentual"]
    )
    pos_y = calcular_posicao(
        altura_personagem,
        nova_altura_icone,
        config["pos_y_percentual"]
    )

    resultado = personagem.copy()
    resultado.paste(icone, (pos_x, pos_y), icone)
    return resultado


def calcular_posicao(tamanho_base, tamanho_item, percentual):
    area_disponivel = max(0, tamanho_base - tamanho_item)
    return int(area_disponivel * (percentual / 100))


def encontrar_icone(pasta_icones, nome):
    for extensao in EXTENSOES_IMAGEM:
        tentativa = os.path.join(pasta_icones, nome + extensao)

        if os.path.exists(tentativa):
            return tentativa

    return None


def mostrar_resumo(total_processadas, erros):
    detalhes = ""

    if erros:
        detalhes = "\n\nOcorrencias:\n" + "\n".join(erros[:12])

        if len(erros) > 12:
            detalhes += f"\n... e mais {len(erros) - 12} ocorrencia(s)."

    messagebox.showinfo(
        "Adicionar icones",
        f"Processamento finalizado!\n\n"
        f"Imagens processadas: {total_processadas}\n"
        f"Erros: {len(erros)}"
        f"{detalhes}"
    )
