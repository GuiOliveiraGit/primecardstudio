import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from banco_cartas import carregar_banco, salvar_carta
from config import EXTENSOES_IMAGEM


def organizar_cartas(janela_pai=None):

    pasta_origem = filedialog.askdirectory(
        title="Selecione a pasta das cartas"
    )

    if not pasta_origem:
        return

    pasta_saida = filedialog.askdirectory(
        title="Selecione onde salvar as cartas organizadas"
    )

    if not pasta_saida:
        return

    modo = escolher_modo_organizacao(janela_pai)

    if not modo:
        return

    banco = carregar_banco()

    arquivos = sorted([
        f for f in os.listdir(pasta_origem)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning(
            "Nenhuma carta",
            "Nenhuma imagem encontrada."
        )
        return

    total = 0

    for arquivo in arquivos:

        nome_arquivo, ext = os.path.splitext(arquivo)
        dados = banco.get(nome_arquivo, {})

        if modo == "Filtro por personagem":

            termo = simpledialog.askstring(
                "Filtro",
                "Digite o nome ou parte do nome do personagem:"
            )

            if not termo:
                return

            termo = termo.lower()

            nome_carta = dados.get("nome", nome_arquivo).lower()

            if termo not in nome_carta and termo not in nome_arquivo.lower():
                continue

            pasta_destino = os.path.join(pasta_saida, "Filtro")

        elif modo == "Agrupar por raridade":

            raridade = dados.get("raridade", "Sem raridade")
            pasta_destino = os.path.join(pasta_saida, raridade)

        elif modo == "Agrupar por expansão":

            expansao = dados.get("expansao", "Sem expansão")
            pasta_destino = os.path.join(pasta_saida, expansao)

        elif modo == "Ordem personalizada":

            ordem = dados.get("ordem", 9999)
            pasta_destino = pasta_saida

            novo_nome = f"{int(ordem):03d}_{arquivo}"

            copiar_arquivo(
                pasta_origem,
                pasta_destino,
                arquivo,
                novo_nome
            )

            total += 1
            continue

        else:
            pasta_destino = pasta_saida

        copiar_arquivo(
            pasta_origem,
            pasta_destino,
            arquivo,
            arquivo
        )

        total += 1

    messagebox.showinfo(
        "Organização concluída",
        f"{total} carta(s) organizadas com sucesso."
    )


def escolher_modo_organizacao(janela_pai=None):

    resultado = {"valor": None}

    janela = tk.Toplevel(janela_pai)
    janela.title("Organizar Cartas")
    janela.geometry("380x330")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Escolha o modo de organização:",
        font=("Arial", 13, "bold")
    ).pack(pady=18)

    opcoes = [
        "Ordem personalizada",
        "Agrupar por raridade",
        "Agrupar por expansão",
        "Filtro por personagem"
    ]

    def escolher(valor):
        resultado["valor"] = valor
        janela.destroy()

    for opcao in opcoes:
        tk.Button(
            janela,
            text=opcao,
            width=30,
            height=2,
            command=lambda o=opcao: escolher(o)
        ).pack(pady=5)

    janela.wait_window()

    return resultado["valor"]


def copiar_arquivo(pasta_origem, pasta_destino, arquivo_origem, arquivo_destino):

    os.makedirs(pasta_destino, exist_ok=True)

    origem = os.path.join(pasta_origem, arquivo_origem)
    destino = os.path.join(pasta_destino, arquivo_destino)

    shutil.copy2(origem, destino)


def editar_metadados_carta(janela_pai=None):

    banco = carregar_banco()

    nome_arquivo = simpledialog.askstring(
        "Carta",
        "Digite o nome do arquivo da carta, sem extensão:\nExemplo: demogorgon"
    )

    if not nome_arquivo:
        return

    dados_atuais = banco.get(nome_arquivo, {})

    ordem = simpledialog.askinteger(
        "Ordem",
        "Digite a ordem da carta:",
        initialvalue=dados_atuais.get("ordem", 9999),
        minvalue=1
    )

    raridade = simpledialog.askstring(
        "Raridade",
        "Digite a raridade:\nExemplo: comum, rara, lendária",
        initialvalue=dados_atuais.get("raridade", "")
    )

    expansao = simpledialog.askstring(
        "Expansão",
        "Digite a expansão:\nExemplo: Mundo Invertido",
        initialvalue=dados_atuais.get("expansao", "")
    )

    salvar_carta(
        nome_arquivo=nome_arquivo,
        quantidade=dados_atuais.get("quantidade")
    )

    banco = carregar_banco()

    if nome_arquivo not in banco:
        banco[nome_arquivo] = {}

    banco[nome_arquivo]["ordem"] = ordem
    banco[nome_arquivo]["raridade"] = raridade
    banco[nome_arquivo]["expansao"] = expansao

    from banco_cartas import salvar_banco
    salvar_banco(banco)

    messagebox.showinfo(
        "Salvo",
        "Metadados da carta salvos com sucesso."
    )
