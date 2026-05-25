from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from banco_cartas import carregar_banco, normalizar_chave
from config import EXTENSOES_IMAGEM
from preferencias import obter_preferencia


def executar_prechecagem(janela_pai=None):
    pasta_frentes = filedialog.askdirectory(
        title="Selecione a pasta das frentes"
    )

    if not pasta_frentes:
        return

    usar_versos = messagebox.askyesno(
        "Versos",
        "Deseja conferir versos correspondentes?"
    )

    pasta_versos = None

    if usar_versos:
        pasta_versos = filedialog.askdirectory(
            title="Selecione a pasta dos versos"
        )

        if not pasta_versos:
            return

    largura_mm = simpledialog.askfloat(
        "Largura da carta",
        "Digite a largura final em mm:",
        minvalue=1,
        initialvalue=obter_preferencia("largura_mm", 63)
    )

    if not largura_mm:
        return

    altura_mm = simpledialog.askfloat(
        "Altura da carta",
        "Digite a altura final em mm:",
        minvalue=1,
        initialvalue=obter_preferencia("altura_mm", 88)
    )

    if not altura_mm:
        return

    relatorio = gerar_relatorio_prechecagem(
        pasta_frentes,
        largura_mm,
        altura_mm,
        pasta_versos
    )

    abrir_janela_relatorio(janela_pai, relatorio)


def gerar_relatorio_prechecagem(
    pasta_frentes,
    largura_mm,
    altura_mm,
    pasta_versos=None
):
    banco = carregar_banco()
    arquivos = listar_imagens(pasta_frentes)

    linhas = [
        "PRE-CHECAGEM DO PROJETO",
        "=" * 55,
        f"Pasta de frentes: {pasta_frentes}",
        f"Tamanho final: {largura_mm} x {altura_mm} mm",
        ""
    ]

    if pasta_versos:
        linhas.append(f"Pasta de versos: {pasta_versos}")
        linhas.append("")

    if not arquivos:
        linhas.append("Nenhuma imagem foi encontrada na pasta de frentes.")
        return "\n".join(linhas)

    nomes_normalizados = {}
    sem_metadados = 0
    versos_ausentes = 0
    alertas_qualidade = 0
    erros_imagem = 0

    for arquivo in arquivos:
        caminho = os.path.join(pasta_frentes, arquivo)
        nome_base = os.path.splitext(arquivo)[0]
        chave = normalizar_chave(nome_base)

        nomes_normalizados.setdefault(chave, []).append(arquivo)

        linhas.append(f"Arquivo: {arquivo}")

        carta = banco.get(chave)
        if not carta:
            sem_metadados += 1
            linhas.append("- Sem metadados no banco_cartas.json.")
        else:
            campos_vazios = campos_importantes_vazios(carta)
            if campos_vazios:
                linhas.append(
                    "- Metadados incompletos: "
                    + ", ".join(campos_vazios)
                )

        if pasta_versos and not encontrar_verso(pasta_versos, nome_base):
            versos_ausentes += 1
            linhas.append("- Verso correspondente nao encontrado.")

        try:
            alertas = analisar_imagem(caminho, largura_mm, altura_mm)
            if alertas:
                alertas_qualidade += 1
                for alerta in alertas:
                    linhas.append(f"- {alerta}")
            else:
                linhas.append("- Qualidade basica: OK.")
        except Exception as erro:
            erros_imagem += 1
            linhas.append(f"- Erro ao abrir imagem: {erro}")

        linhas.append("-" * 55)

    duplicados = {
        chave: nomes
        for chave, nomes in nomes_normalizados.items()
        if len(nomes) > 1
    }

    linhas.append("")
    linhas.append("RESUMO")
    linhas.append("=" * 55)
    linhas.append(f"Frentes analisadas: {len(arquivos)}")
    linhas.append(f"Sem metadados: {sem_metadados}")
    linhas.append(f"Versos ausentes: {versos_ausentes}")
    linhas.append(f"Com alerta de qualidade: {alertas_qualidade}")
    linhas.append(f"Com erro de leitura: {erros_imagem}")
    linhas.append(f"Nomes normalizados duplicados: {len(duplicados)}")

    if duplicados:
        linhas.append("")
        linhas.append("DUPLICADOS")
        for chave, nomes in duplicados.items():
            linhas.append(f"- {chave}: {', '.join(nomes)}")

    return "\n".join(linhas)


def listar_imagens(pasta):
    return sorted([
        arquivo for arquivo in os.listdir(pasta)
        if os.path.splitext(arquivo)[1].lower() in EXTENSOES_IMAGEM
    ])


def encontrar_verso(pasta_versos, nome_base):
    for extensao in EXTENSOES_IMAGEM:
        caminho = os.path.join(pasta_versos, nome_base + extensao)

        if os.path.exists(caminho):
            return caminho

    return None


def campos_importantes_vazios(carta):
    campos = []

    for campo in ["nome", "subtitulo", "habilidades"]:
        valor = carta.get(campo)

        if valor in (None, "", []):
            campos.append(campo)

    return campos


def analisar_imagem(caminho, largura_mm, altura_mm):
    alertas = []

    with Image.open(caminho) as imagem:
        largura_px, altura_px = imagem.size

    dpi_x = largura_px / (largura_mm / 25.4)
    dpi_y = altura_px / (altura_mm / 25.4)
    dpi_estimado = min(dpi_x, dpi_y)

    proporcao_img = largura_px / altura_px
    proporcao_carta = largura_mm / altura_mm
    diferenca_percentual = abs(
        ((proporcao_img - proporcao_carta) / proporcao_carta) * 100
    )

    if dpi_estimado < 300:
        alertas.append(f"DPI estimado abaixo de 300: {dpi_estimado:.0f}.")

    if diferenca_percentual > 3:
        alertas.append(
            f"Proporcao fora do esperado em {diferenca_percentual:.2f}%."
        )

    if largura_px < 1000 or altura_px < 1400:
        alertas.append(
            f"Resolucao baixa para impressao: {largura_px} x {altura_px} px."
        )

    return alertas


def abrir_janela_relatorio(janela_pai, texto):
    janela = tk.Toplevel(janela_pai)
    janela.title("Pre-checagem do Projeto")
    janela.geometry("780x620")

    caixa_texto = tk.Text(janela, wrap="word", font=("Consolas", 10))
    caixa_texto.pack(fill="both", expand=True, padx=10, pady=10)
    caixa_texto.insert("1.0", texto)
    caixa_texto.config(state="disabled")

    def salvar_relatorio():
        caminho = filedialog.asksaveasfilename(
            title="Salvar relatorio",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")]
        )

        if not caminho:
            return

        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)

        messagebox.showinfo(
            "Relatorio salvo",
            "Relatorio salvo com sucesso."
        )

    tk.Button(
        janela,
        text="Salvar relatorio em TXT",
        font=("Arial", 11),
        command=salvar_relatorio
    ).pack(pady=8)
