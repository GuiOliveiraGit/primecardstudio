import os
import tkinter as tk
from tkinter import filedialog, messagebox

from banco_cartas import obter_carta, salvar_carta
from config import TIPOS_ARQUIVO_IMAGEM
from preview_global import carregar_imagem_preview


def abrir_editor_carta(janela_pai=None):
    caminho = filedialog.askopenfilename(
        title="Selecione a carta",
        filetypes=TIPOS_ARQUIVO_IMAGEM
    )

    if not caminho:
        return

    nome_arquivo = os.path.splitext(os.path.basename(caminho))[0]
    carta = obter_carta(nome_arquivo)

    janela = tk.Toplevel(janela_pai)
    janela.title(f"Editor da carta - {nome_arquivo}")
    janela.geometry("900x620")
    janela.grab_set()

    frame_preview = tk.Frame(janela)
    frame_preview.pack(side="left", fill="both", expand=True, padx=14, pady=14)

    frame_form = tk.Frame(janela)
    frame_form.pack(side="right", fill="y", padx=14, pady=14)

    tk.Label(
        frame_form,
        text="Dados da carta",
        font=("Arial", 15, "bold")
    ).pack(anchor="w", pady=(0, 12))

    foto = carregar_imagem_preview(caminho, 430, 560)
    preview = tk.Label(frame_preview, image=foto, bg="#222222")
    preview.image = foto
    preview.pack(expand=True)

    entradas = {}

    def campo(rotulo, chave, largura=34):
        tk.Label(frame_form, text=rotulo).pack(anchor="w", pady=(6, 0))
        entrada = tk.Entry(frame_form, width=largura)
        entrada.insert(0, str(carta.get(chave, "")))
        entrada.pack(anchor="w")
        entradas[chave] = entrada

    campo("Nome", "nome")
    campo("Subtitulo", "subtitulo")
    campo("Cor", "cor")
    campo("Estilo", "estilo")
    campo("Quantidade", "quantidade")
    campo("Raridade", "raridade")
    campo("Expansao", "expansao")
    campo("Ordem", "ordem")

    tk.Label(
        frame_form,
        text="Habilidades: uma por linha, formato nome | descricao"
    ).pack(anchor="w", pady=(10, 0))

    texto_habilidades = tk.Text(frame_form, width=38, height=8)
    texto_habilidades.pack(anchor="w")

    habilidades = carta.get("habilidades", [])
    linhas_habilidades = [
        f"{item.get('nome', '')} | {item.get('descricao', '')}"
        for item in habilidades
    ]
    texto_habilidades.insert("1.0", "\n".join(linhas_habilidades))

    def salvar():
        try:
            quantidade = int(entradas["quantidade"].get() or 1)
        except ValueError:
            messagebox.showerror("Editor", "Quantidade precisa ser um numero.")
            return

        try:
            ordem = int(entradas["ordem"].get() or 9999)
        except ValueError:
            messagebox.showerror("Editor", "Ordem precisa ser um numero.")
            return

        habilidades = parse_habilidades(texto_habilidades.get("1.0", "end"))

        salvar_carta(
            nome_arquivo=nome_arquivo,
            nome=entradas["nome"].get().strip(),
            subtitulo=entradas["subtitulo"].get().strip(),
            cor=entradas["cor"].get().strip(),
            estilo=entradas["estilo"].get().strip(),
            quantidade=quantidade,
            raridade=entradas["raridade"].get().strip(),
            expansao=entradas["expansao"].get().strip(),
            ordem=ordem,
            habilidades=habilidades
        )

        messagebox.showinfo("Editor", "Carta salva no banco.")
        janela.destroy()

    tk.Button(
        frame_form,
        text="Salvar carta",
        width=24,
        command=salvar
    ).pack(anchor="w", pady=16)


def parse_habilidades(texto):
    habilidades = []

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            continue

        if "|" in linha:
            nome, descricao = linha.split("|", 1)
        else:
            nome, descricao = linha, ""

        habilidades.append({
            "nome": nome.strip(),
            "descricao": descricao.strip()
        })

    return habilidades
