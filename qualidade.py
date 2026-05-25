from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from config import EXTENSOES_IMAGEM
from progresso import JanelaProgresso


def verificar_qualidade_impressao(janela_pai=None):

    pasta_imagens = filedialog.askdirectory(
        title="Selecione a pasta das cartas"
    )

    if not pasta_imagens:
        return

    largura_mm = simpledialog.askfloat(
        "Largura da carta",
        "Digite a largura final da carta em mm:\nExemplo: 61",
        minvalue=1
    )

    if not largura_mm:
        return

    altura_mm = simpledialog.askfloat(
        "Altura da carta",
        "Digite a altura final da carta em mm:\nExemplo: 91",
        minvalue=1
    )

    if not altura_mm:
        return

    arquivos = sorted([
        f for f in os.listdir(pasta_imagens)
        if os.path.splitext(f)[1].lower() in EXTENSOES_IMAGEM
    ])

    if not arquivos:
        messagebox.showwarning(
            "Nenhuma imagem",
            "Nenhuma imagem encontrada na pasta selecionada."
        )
        return

    relatorio = []

    relatorio.append("RELATÓRIO DE QUALIDADE PARA IMPRESSÃO")
    relatorio.append("=" * 55)
    relatorio.append(f"Tamanho final escolhido: {largura_mm} x {altura_mm} mm")
    relatorio.append("")

    total_ok = 0
    total_alerta = 0
    total_ruim = 0

    progresso = JanelaProgresso(
        janela_pai,
        "Verificar qualidade",
        len(arquivos)
    )

    for indice, arquivo in enumerate(arquivos, start=1):
        progresso.atualizar(indice, f"Analisando {arquivo}")

        caminho = os.path.join(pasta_imagens, arquivo)

        try:
            img = Image.open(caminho)

            largura_px, altura_px = img.size

            dpi_x = largura_px / (largura_mm / 25.4)
            dpi_y = altura_px / (altura_mm / 25.4)

            dpi_estimado = min(dpi_x, dpi_y)

            proporcao_img = largura_px / altura_px
            proporcao_carta = largura_mm / altura_mm

            diferenca_percentual = (
                (proporcao_img - proporcao_carta)
                / proporcao_carta
            ) * 100

            status = "OK"
            avisos = []

            # ====================================================
            # VERIFICA DPI
            # ====================================================

            if dpi_estimado >= 300:
                status = "OK"
                total_ok += 1

            elif dpi_estimado >= 220:
                status = "ATENÇÃO"
                total_alerta += 1
                avisos.append(
                    "DPI abaixo de 300. Pode imprimir aceitável, mas não é ideal."
                )

            else:
                status = "RUIM"
                total_ruim += 1
                avisos.append(
                    "DPI muito baixo. Alto risco de serrilhado/perda de nitidez."
                )

            # ====================================================
            # VERIFICA PROPORÇÃO
            # ====================================================

            if abs(diferenca_percentual) > 3:

                if status == "OK":
                    total_ok -= 1
                    total_alerta += 1
                    status = "ATENÇÃO"

                if diferenca_percentual > 0:
                    avisos.append(
                        f"Proporção fora em {abs(diferenca_percentual):.2f}%. "
                        f"A imagem está mais larga do que o tamanho escolhido."
                    )
                else:
                    avisos.append(
                        f"Proporção fora em {abs(diferenca_percentual):.2f}%. "
                        f"A imagem está mais alta/estreita do que o tamanho escolhido."
                    )

                avisos.append(
                    "A imagem pode ser cortada ou deformada ao encaixar no tamanho escolhido."
                )

            # ====================================================
            # VERIFICA RESOLUÇÃO ABSOLUTA
            # ====================================================

            if largura_px < 1000 or altura_px < 1400:

                if status == "OK":
                    total_ok -= 1
                    total_alerta += 1
                    status = "ATENÇÃO"

                avisos.append(
                    "Resolução em pixels baixa para carta impressa."
                )

            # ====================================================
            # RELATÓRIO DA CARTA
            # ====================================================

            relatorio.append(f"Arquivo: {arquivo}")
            relatorio.append(f"Status: {status}")
            relatorio.append(f"Resolução: {largura_px} x {altura_px} px")
            relatorio.append(f"DPI estimado: {dpi_estimado:.0f}")
            relatorio.append(f"DPI horizontal: {dpi_x:.0f}")
            relatorio.append(f"DPI vertical: {dpi_y:.0f}")
            relatorio.append(f"Proporção da imagem: {proporcao_img:.4f}")
            relatorio.append(f"Proporção esperada: {proporcao_carta:.4f}")
            relatorio.append(
                f"Diferença de proporção: {diferenca_percentual:+.2f}%"
            )

            if diferenca_percentual > 0:
                relatorio.append(
                    "Onde está fora: largura proporcionalmente maior."
                )
            elif diferenca_percentual < 0:
                relatorio.append(
                    "Onde está fora: altura proporcionalmente maior / imagem mais estreita."
                )
            else:
                relatorio.append(
                    "Onde está fora: proporção igual ao tamanho escolhido."
                )

            if avisos:
                relatorio.append("Avisos:")
                for aviso in avisos:
                    relatorio.append(f"- {aviso}")

            relatorio.append("-" * 55)

        except Exception as e:

            total_ruim += 1

            relatorio.append(f"Arquivo: {arquivo}")
            relatorio.append("Status: ERRO")
            relatorio.append(f"Erro ao abrir imagem: {e}")
            relatorio.append("-" * 55)

    progresso.fechar()

    # ============================================================
    # RESUMO FINAL
    # ============================================================

    relatorio.append("")
    relatorio.append("RESUMO")
    relatorio.append("=" * 55)
    relatorio.append(f"OK: {total_ok}")
    relatorio.append(f"Atenção: {total_alerta}")
    relatorio.append(f"Ruim: {total_ruim}")

    abrir_janela_relatorio(
        janela_pai,
        "\n".join(relatorio)
    )


def abrir_janela_relatorio(janela_pai, texto):

    janela = tk.Toplevel(janela_pai)
    janela.title("Relatório de Qualidade")
    janela.geometry("760x620")

    caixa_texto = tk.Text(
        janela,
        wrap="word",
        font=("Consolas", 10)
    )

    caixa_texto.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    caixa_texto.insert("1.0", texto)
    caixa_texto.config(state="disabled")

    def salvar_relatorio():

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")]
        )

        if not caminho:
            return

        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)

        messagebox.showinfo(
            "Relatório salvo",
            "Relatório salvo com sucesso."
        )

    botao_salvar = tk.Button(
        janela,
        text="Salvar relatório em TXT",
        font=("Arial", 11),
        command=salvar_relatorio
    )

    botao_salvar.pack(pady=8)
