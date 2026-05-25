from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def carregar_imagem_preview(caminho, largura_max=620, altura_max=430):
    caminho = caminho.strip().replace("{", "").replace("}", "")

    if not os.path.exists(caminho):
        return None

    img = Image.open(caminho).convert("RGBA")

    largura, altura = img.size
    proporcao = largura / altura

    if largura >= altura:
        nova_largura = largura_max
        nova_altura = int(nova_largura / proporcao)

        if nova_altura > altura_max:
            nova_altura = altura_max
            nova_largura = int(nova_altura * proporcao)

    else:
        nova_altura = altura_max
        nova_largura = int(nova_altura * proporcao)

        if nova_largura > largura_max:
            nova_largura = largura_max
            nova_altura = int(nova_largura / proporcao)

    img = img.resize(
        (nova_largura, nova_altura),
        Image.LANCZOS
    )

    return ImageTk.PhotoImage(img)


def criar_preview_global(
    parent,
    titulo="Preview",
    largura_max=620,
    altura_max=430
):
    frame = tk.Frame(
        parent,
        bg="#242424",
        padx=20,
        pady=18
    )

    frame.pack(
        fill="both",
        expand=True,
        pady=10
    )

    tk.Label(
        frame,
        text=f"🖼️ {titulo}",
        bg="#242424",
        fg="#F2F2F2",
        font=("Arial", 15, "bold")
    ).pack(pady=(0, 5))

    label_info = tk.Label(
        frame,
        text="Selecione ou arraste uma imagem para visualizar.",
        bg="#242424",
        fg="#B8B8B8",
        font=("Arial", 10)
    )

    label_info.pack(pady=(0, 8))

    # FIX: sem width/height em caracteres; tamanho definido em pixels via
    # width e height só após carregar imagem. O label cresce com a foto.
    label_preview = tk.Label(
        frame,
        bg="#181818",
        fg="#777777",
        text="Nenhuma imagem selecionada",
        anchor="center",
        width=largura_max,       # pixels — só tem efeito antes da imagem
        height=altura_max,
    )

    # Força o label a usar pixels (não caracteres) ao definir um bitmap vazio
    label_preview.config(width=largura_max, height=altura_max)

    preview_ref = {
        "foto": None,
        "caminho": None,
        "label": label_preview,
        "info": label_info
    }

    def atualizar_preview(caminho):
        try:
            foto = carregar_imagem_preview(
                caminho,
                largura_max,
                altura_max
            )

            if foto is None:
                return

            # FIX: remove as dimensões fixas em caracteres antes de exibir
            # a imagem, assim o label se ajusta ao tamanho real da foto.
            label_preview.config(
                image=foto,
                text="",
                width=foto.width(),
                height=foto.height()
            )

            # Mantém referência para evitar garbage collection
            label_preview.image = foto

            preview_ref["foto"] = foto
            preview_ref["caminho"] = caminho

            label_info.config(
                text=f"Preview: {os.path.basename(caminho)}"
            )

        except Exception as e:
            messagebox.showerror(
                "Erro no preview",
                f"Não foi possível carregar o preview:\n{e}"
            )

    def selecionar_imagem():
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.webp")
            ]
        )

        if caminho:
            atualizar_preview(caminho)

    botao = tk.Button(
        frame,
        text="Selecionar imagem",
        command=selecionar_imagem,
        bg="#C30212",
        fg="white",
        activebackground="#A0000E",
        activeforeground="white",
        relief="flat",
        padx=18,
        pady=10,
        font=("Arial", 11, "bold"),
        cursor="hand2"
    )

    botao.pack(pady=(0, 12))

    label_preview.pack(pady=(0, 8))

    preview_ref["atualizar"] = atualizar_preview

    return preview_ref
