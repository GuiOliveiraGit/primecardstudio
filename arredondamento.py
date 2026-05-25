from PIL import Image, ImageDraw, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from config import EXTENSOES_IMAGEM
from progresso import JanelaProgresso


def arredondar_cantos_cartas(janela_pai=None):

    pasta_imagens = filedialog.askdirectory(
        title="Selecione a pasta das cartas"
    )
    if not pasta_imagens:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione onde salvar as cartas arredondadas"
    )
    if not pasta_saida:
        return

    largura_mm = simpledialog.askfloat(
        "Largura da carta",
        "Digite a largura da carta em mm:\nExemplo: 63",
        minvalue=1
    )
    if not largura_mm:
        return

    altura_mm = simpledialog.askfloat(
        "Altura da carta",
        "Digite a altura da carta em mm:\nExemplo: 88",
        minvalue=1
    )
    if not altura_mm:
        return

    preset = escolher_preset_arredondamento(janela_pai)
    if not preset:
        return

    if preset == "Magic":
        raio_mm = 3.0
    elif preset == "Coup":
        raio_mm = 3.5
    else:
        raio_mm = simpledialog.askfloat(
            "Raio personalizado",
            "Digite o raio do canto em mm:",
            minvalue=0,
            initialvalue=3
        )
        if raio_mm is None:
            return

    arquivos = sorted([
        f for f in os.listdir(pasta_imagens)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning(
            "Nenhuma imagem",
            "Nenhuma carta encontrada."
        )
        return

    primeira_imagem = os.path.join(pasta_imagens, arquivos[0])

    confirmar = mostrar_preview_arredondamento(
        janela_pai,
        primeira_imagem,
        largura_mm,
        altura_mm,
        raio_mm,
        preset
    )

    if not confirmar:
        return

    total = 0
    erros = []
    progresso = JanelaProgresso(
        janela_pai,
        "Arredondar cantos",
        len(arquivos)
    )

    for indice, arquivo in enumerate(arquivos, start=1):
        progresso.atualizar(indice, f"Processando {arquivo}")

        caminho = os.path.join(pasta_imagens, arquivo)
        nome, ext = os.path.splitext(arquivo)

        try:
            imagem = Image.open(caminho).convert("RGBA")

            resultado = aplicar_arredondamento(
                imagem,
                largura_mm,
                altura_mm,
                raio_mm
            )

            caminho_saida = os.path.join(
                pasta_saida,
                f"{nome}_arredondado.png"
            )

            resultado.save(caminho_saida)
            total += 1

        except Exception as e:
            erros.append(f"Erro em {arquivo}: {e}")

    progresso.fechar()

    detalhes = ""

    if erros:
        detalhes = "\n\nOcorrencias:\n" + "\n".join(erros[:12])

        if len(erros) > 12:
            detalhes += f"\n... e mais {len(erros) - 12} ocorrencia(s)."

    messagebox.showinfo(
        "Concluído",
        f"Cantos arredondados aplicados em {total} carta(s).\n"
        f"Erros: {len(erros)}"
        f"{detalhes}"
    )


def escolher_preset_arredondamento(janela_pai=None):

    resultado = {"valor": None}

    janela = tk.Toplevel(janela_pai)
    janela.title("Padrão de Arredondamento")
    janela.geometry("360x250")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Escolha o padrão de canto:",
        font=("Arial", 13, "bold")
    ).pack(pady=18)

    def escolher(valor):
        resultado["valor"] = valor
        janela.destroy()

    tk.Button(
        janela,
        text="Magic — 3 mm",
        width=26,
        height=2,
        command=lambda: escolher("Magic")
    ).pack(pady=6)

    tk.Button(
        janela,
        text="Coup — 3,5 mm",
        width=26,
        height=2,
        command=lambda: escolher("Coup")
    ).pack(pady=6)

    tk.Button(
        janela,
        text="Personalizado",
        width=26,
        height=2,
        command=lambda: escolher("Personalizado")
    ).pack(pady=6)

    janela.wait_window()

    return resultado["valor"]


def aplicar_arredondamento(imagem, largura_mm, altura_mm, raio_mm):

    largura_px, altura_px = imagem.size

    px_por_mm_x = largura_px / largura_mm
    px_por_mm_y = altura_px / altura_mm

    px_por_mm = (px_por_mm_x + px_por_mm_y) / 2

    raio_px = int(raio_mm * px_por_mm)

    mascara = Image.new("L", imagem.size, 0)
    draw = ImageDraw.Draw(mascara)

    draw.rounded_rectangle(
        [0, 0, largura_px, altura_px],
        radius=raio_px,
        fill=255
    )

    resultado = Image.new("RGBA", imagem.size, (0, 0, 0, 0))
    resultado.paste(imagem, (0, 0), mascara)

    return resultado


def mostrar_preview_arredondamento(
    janela_pai,
    caminho_imagem,
    largura_mm,
    altura_mm,
    raio_mm,
    preset
):

    resultado = {"confirmar": False}

    imagem = Image.open(caminho_imagem).convert("RGBA")

    arredondada = aplicar_arredondamento(
        imagem,
        largura_mm,
        altura_mm,
        raio_mm
    )

    preview = arredondada.copy()
    preview.thumbnail((420, 520), Image.LANCZOS)

    janela = tk.Toplevel(janela_pai)
    janela.title("Preview do Corte")
    janela.geometry("520x680")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Preview do Arredondamento",
        font=("Arial", 15, "bold")
    ).pack(pady=(15, 5))

    tk.Label(
        janela,
        text=f"Padrão: {preset} | Raio: {raio_mm} mm",
        font=("Arial", 11)
    ).pack(pady=(0, 10))

    foto = ImageTk.PhotoImage(preview)

    label = tk.Label(janela, image=foto, bg="#222222")
    label.image = foto
    label.pack(pady=10)

    tk.Label(
        janela,
        text="A área transparente representa o corte arredondado.",
        font=("Arial", 10),
        fg="gray"
    ).pack(pady=5)

    def confirmar():
        resultado["confirmar"] = True
        janela.destroy()

    def cancelar():
        janela.destroy()

    frame = tk.Frame(janela)
    frame.pack(pady=15)

    tk.Button(
        frame,
        text="Confirmar",
        width=16,
        height=2,
        command=confirmar
    ).pack(side="left", padx=8)

    tk.Button(
        frame,
        text="Cancelar",
        width=16,
        height=2,
        command=cancelar
    ).pack(side="left", padx=8)

    janela.wait_window()

    return resultado["confirmar"]
