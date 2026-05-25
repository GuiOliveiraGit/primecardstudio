
from curvas import exportar_pdf_com_texto_em_curvas
from vetorial import exportar_pdf_vetorial
from exportacao import exportar_profissional
from organizacao import organizar_cartas, editar_metadados_carta
from automacao import importar_csv_cartas
from preview_global import criar_preview_global
from arredondamento import arredondar_cantos_cartas

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

from icones import adicionar_icones
from nome import criar_caixa_nome_magic
from habilidades import adicionar_habilidades
from pdf_grafica import gerar_pdf_grafica
from qualidade import verificar_qualidade_impressao
from prechecagem import executar_prechecagem
from configuracoes import abrir_configuracoes
from projeto import abrir_gerenciador_projeto
from ambiente import verificar_ambiente
from editor_carta import abrir_editor_carta

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_ATIVO = True
except Exception:
    DND_ATIVO = False


# ============================================================
# CORES DO TEMA
# ============================================================

COR_FUNDO        = "#121212"
COR_SIDEBAR      = "#1E1E1E"
COR_CARD         = "#242424"
COR_TEXTO        = "#F2F2F2"
COR_TEXTO_SEC    = "#B8B8B8"
COR_DESTAQUE     = "#C30212"
COR_BOTAO        = "#2D2D2D"
COR_BOTAO_HOVER  = "#3A3A3A"


# ============================================================
# JANELA PRINCIPAL
# ============================================================

if DND_ATIVO:
    try:
        janela = TkinterDnD.Tk()
    except Exception:
        DND_ATIVO = False
        janela = tk.Tk()
else:
    janela = tk.Tk()

janela.title("PrimeStudio Card")
janela.geometry("1050x720")
janela.minsize(950, 650)
janela.configure(bg=COR_FUNDO)


# ============================================================
# VARIÁVEIS GLOBAIS
# ============================================================

imagem_preview_ref = {"foto": None}
caminho_preview    = {"valor": None}


# ============================================================
# FUNÇÕES DE INTERFACE
# ============================================================

def limpar_conteudo():
    for widget in frame_conteudo.winfo_children():
        widget.destroy()


def atualizar_descricao(texto):
    descricao_var.set(texto)


def criar_botao_painel(parent, texto, comando, icone="", descricao=""):
    """
    Cria botão alinhado com área fixa para ícone.
    Também atualiza a descrição ao passar o mouse.
    """

    frame_botao = tk.Frame(
        parent,
        bg=COR_BOTAO,
        height=50,
        cursor="hand2"
    )

    frame_botao.pack(fill="x", pady=3)
    frame_botao.pack_propagate(False)

    frame_icone = tk.Frame(
        frame_botao,
        bg=COR_BOTAO,
        width=44,
        cursor="hand2"
    )

    frame_icone.pack(side="left", fill="y")
    frame_icone.pack_propagate(False)

    label_icone = tk.Label(
        frame_icone,
        text=icone,
        bg=COR_BOTAO,
        fg=COR_TEXTO,
        font=("Segoe UI Emoji", 13),
        anchor="center",
        cursor="hand2"
    )

    label_icone.place(relx=0.5, rely=0.5, anchor="center")

    label_texto = tk.Label(
        frame_botao,
        text=texto,
        bg=COR_BOTAO,
        fg=COR_TEXTO,
        font=("Arial", 11, "bold"),
        anchor="w",
        cursor="hand2"
    )

    label_texto.pack(side="left", fill="both", expand=True, padx=(4, 12))

    tk.Frame(
        frame_botao,
        bg="#3D3D3D",
        width=1
    ).place(x=44, y=8, height=34)

    def clicar(event=None):
        comando()

    def entrar(event=None):
        for w in [frame_botao, frame_icone, label_icone, label_texto]:
            w.config(bg=COR_BOTAO_HOVER)

        if descricao:
            atualizar_descricao(descricao)

    def sair(event=None):
        for w in [frame_botao, frame_icone, label_icone, label_texto]:
            w.config(bg=COR_BOTAO)

        atualizar_descricao(
            "Passe o mouse sobre uma opção para ver o que ela faz e quais arquivos ela espera."
        )

    for widget in [frame_botao, frame_icone, label_icone, label_texto]:
        widget.bind("<Button-1>", clicar)
        widget.bind("<Enter>", entrar)
        widget.bind("<Leave>", sair)

    return frame_botao


def criar_area_preview(parent):
    return criar_preview_global(
        parent,
        titulo="Preview grande",
        largura_max=620,
        altura_max=430
    )


# ============================================================
# TELAS
# ============================================================

def mostrar_tela_inicio():
    limpar_conteudo()

    tk.Label(
        frame_conteudo,
        text="PrimeStudio Card",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 27, "bold")
    ).pack(anchor="w", pady=(10, 5))

    tk.Label(
        frame_conteudo,
        text="Editor de cartas, impressão e preparação de arquivos.",
        bg=COR_FUNDO,
        fg=COR_TEXTO_SEC,
        font=("Arial", 12)
    ).pack(anchor="w", pady=(0, 18))

    criar_area_preview(frame_conteudo)


def mostrar_tela_criacao():
    limpar_conteudo()

    tk.Label(
        frame_conteudo,
        text="Criação das Cartas",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 24, "bold")
    ).pack(anchor="w", pady=(10, 5))

    tk.Label(
        frame_conteudo,
        text="Adicione ícones, nomes, subtítulos e habilidades.",
        bg=COR_FUNDO,
        fg=COR_TEXTO_SEC,
        font=("Arial", 12)
    ).pack(anchor="w", pady=(0, 18))

    frame_botoes = tk.Frame(frame_conteudo, bg=COR_FUNDO)
    frame_botoes.pack(fill="x")

    criar_botao_painel(
        frame_botoes,
        "Adicionar Ícones",
        lambda: adicionar_icones(janela),
        "🎯",
        "Adiciona ícones no canto superior direito das cartas. Espera imagens PNG, JPG, JPEG ou WEBP e uma pasta de ícones com nomes iguais aos arquivos das cartas."
    )

    criar_botao_painel(
        frame_botoes,
        "Criar Caixa de Nome Magic",
        lambda: criar_caixa_nome_magic(janela),
        "🏷️",
        "Cria a caixa de nome no topo da carta, estilo Magic. Espera imagens PNG, JPG, JPEG ou WEBP."
    )

    criar_botao_painel(
        frame_botoes,
        "Adicionar Subtítulo e Ataques",
        lambda: adicionar_habilidades(janela),
        "⚔️",
        "Adiciona subtítulo, ataques e habilidades. Espera imagens PNG, JPG, JPEG ou WEBP e salva os dados no banco_cartas.json."
    )

    criar_botao_painel(
        frame_botoes,
        "Importar Cartas por CSV",
        lambda: importar_csv_cartas(janela),
        "📊",
        "Importa dados das cartas por CSV. Espera arquivo .CSV com campos como arquivo, nome, subtítulo, cor, estilo, quantidade e ataques."
    )

    criar_botao_painel(
        frame_botoes,
        "Editor Central da Carta",
        lambda: abrir_editor_carta(janela),
        "ED",
        "Edita imagem, nome, subtitulo, habilidades, quantidade e metadados em uma unica tela."
    )

    criar_area_preview(frame_conteudo)


def mostrar_tela_impressao():
    limpar_conteudo()

    tk.Label(
        frame_conteudo,
        text="Impressão e PDF",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 24, "bold")
    ).pack(anchor="w", pady=(10, 5))

    tk.Label(
        frame_conteudo,
        text="Gere PDFs, alinhe frente e verso e confira qualidade.",
        bg=COR_FUNDO,
        fg=COR_TEXTO_SEC,
        font=("Arial", 12)
    ).pack(anchor="w", pady=(0, 18))

    frame_botoes = tk.Frame(frame_conteudo, bg=COR_FUNDO)
    frame_botoes.pack(fill="x")

    criar_botao_painel(
        frame_botoes,
        "Gerar PDF para Recorte",
        lambda: gerar_pdf_grafica(janela),
        "📄",
        "Gera PDF em A4 com frentes, versos, pontilhado, margem segura, sangria e marcas de corte. Espera imagens PNG, JPG, JPEG ou WEBP."
    )

    criar_botao_painel(
        frame_botoes,
        "Configuracoes de Impressao",
        lambda: abrir_configuracoes(janela),
        "CFG",
        "Define tamanho, sangria, margem segura, espacamento e quantidade padrao."
    )

    criar_botao_painel(
        frame_botoes,
        "Verificar Qualidade",
        lambda: verificar_qualidade_impressao(janela),
        "🔍",
        "Analisa DPI estimado, resolução, proporção da imagem e risco de serrilhado. Espera imagens PNG, JPG, JPEG ou WEBP."
    )

    criar_botao_painel(
        frame_botoes,
        "Pre-checagem do Projeto",
        lambda: executar_prechecagem(janela),
        "OK",
        "Confere metadados, versos correspondentes, nomes duplicados, DPI, resolucao e proporcao antes de fechar o PDF."
    )

    criar_botao_painel(
        frame_botoes,
        "Arredondar Cantos",
        lambda: arredondar_cantos_cartas(janela),
        "⭕",
        "Aplica cantos arredondados nas cartas com raio configurável. Espera imagens PNG, JPG, JPEG ou WEBP."
    )

    criar_botao_painel(
        frame_botoes,
        "Organizar Cartas",
        lambda: organizar_cartas(janela),
        "🗂️",
        "Organiza cartas por ordem, raridade, expansão ou personagem. Espera imagens PNG, JPG, JPEG ou WEBP e usa dados do banco_cartas.json."
    )

    criar_botao_painel(
        frame_botoes,
        "Editar Metadados da Carta",
        lambda: editar_metadados_carta(janela),
        "📝",
        "Edita dados como ordem, raridade e expansão no banco_cartas.json."
    )

    criar_botao_painel(
        frame_botoes,
        "Exportação Profissional",
        lambda: exportar_profissional(janela),
        "📦",
        "Exporta imagens para PNG, PDF, TIFF, SVG simples ou prepara etapa futura para PDF/X. Espera imagens PNG, JPG, JPEG ou WEBP."
    )

    criar_botao_painel(
        frame_botoes,
        "PDF Vetorial",
        lambda: exportar_pdf_vetorial(janela),
        "🖋️",
        "Gera PDF com texto vetorial real desenhado no PDF. Espera uma imagem base e textos definidos pelo usuário."
    )

    criar_botao_painel(
        frame_botoes,
        "PDF com Texto em Curvas",
        lambda: exportar_pdf_com_texto_em_curvas(janela),
        "✒️",
        "Gera PDF com textos convertidos em curvas reais, puxando nome, subtítulo e ataques do banco_cartas.json. Espera artes sem texto em PNG, JPG, JPEG ou WEBP."
    )

    criar_area_preview(frame_conteudo)


def mostrar_tela_sistema():
    limpar_conteudo()

    tk.Label(
        frame_conteudo,
        text="Sistema",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 24, "bold")
    ).pack(anchor="w", pady=(10, 5))

    tk.Label(
        frame_conteudo,
        text="Configurações e informações do software.",
        bg=COR_FUNDO,
        fg=COR_TEXTO_SEC,
        font=("Arial", 12)
    ).pack(anchor="w", pady=(0, 18))

    info = (
        "Estrutura atual:\n\n"
        "main.py\n"
        "icones.py\n"
        "nome.py\n"
        "habilidades.py\n"
        "pdf_grafica.py\n"
        "qualidade.py\n"
        "presets.py\n"
        "templates.py\n"
        "banco_cartas.py\n"
        "curvas.py\n"
        "vetorial.py\n"
        "exportacao.py\n"
        "organizacao.py\n"
        "automacao.py\n"
        "preview_global.py\n"
        "arredondamento.py\n"
        "config.py\n"
        "preferencias.py\n"
        "prechecagem.py\n"
        "configuracoes.py\n"
        "projeto.py\n"
        "ambiente.py\n"
        "editor_carta.py\n"
        "progresso.py"
    )

    tk.Label(
        frame_conteudo,
        text=info,
        justify="left",
        bg=COR_CARD,
        fg=COR_TEXTO,
        font=("Consolas", 11),
        padx=20,
        pady=20
    ).pack(anchor="w", fill="x", pady=10)

    criar_botao_painel(
        frame_conteudo,
        "Gerenciar Projeto",
        lambda: abrir_gerenciador_projeto(janela),
        "PRJ",
        "Salva nome do projeto, pasta de frentes, pasta de versos e pasta de saida."
    )

    criar_botao_painel(
        frame_conteudo,
        "Configuracoes",
        lambda: abrir_configuracoes(janela),
        "CFG",
        "Abre preferencias de impressao e exportacao."
    )

    criar_botao_painel(
        frame_conteudo,
        "Validar Ambiente",
        lambda: verificar_ambiente(janela),
        "CHK",
        "Confere Python e dependencias instaladas para rodar e empacotar o app."
    )

    criar_botao_painel(
        frame_conteudo,
        "Sair",
        janela.destroy,
        "🚪",
        "Fecha o PrimeStudio Card."
    )


# ============================================================
# LAYOUT PRINCIPAL
# ============================================================

frame_sidebar = tk.Frame(janela, bg=COR_SIDEBAR, width=230)
frame_sidebar.pack(side="left", fill="y")
frame_sidebar.pack_propagate(False)

frame_conteudo = tk.Frame(janela, bg=COR_FUNDO)
frame_conteudo.pack(side="right", fill="both", expand=True, padx=25, pady=20)


# ============================================================
# SIDEBAR
# ============================================================

tk.Label(
    frame_sidebar,
    text="PRIMESTUDIO",
    bg=COR_SIDEBAR,
    fg=COR_DESTAQUE,
    font=("Arial", 17, "bold")
).pack(anchor="w", padx=24, pady=(28, 0))

tk.Label(
    frame_sidebar,
    text="Card",
    bg=COR_SIDEBAR,
    fg=COR_TEXTO_SEC,
    font=("Arial", 11, "bold")
).pack(anchor="w", padx=24, pady=(0, 22))

tk.Frame(
    frame_sidebar,
    bg="#2E2E2E",
    height=1
).pack(fill="x", padx=12, pady=(0, 10))

criar_botao_painel(
    frame_sidebar,
    "Início",
    mostrar_tela_inicio,
    "🏠",
    "Tela inicial do software. Mostra o preview global e acesso rápido ao projeto."
)

criar_botao_painel(
    frame_sidebar,
    "Criação",
    mostrar_tela_criacao,
    "🎨",
    "Funções para criar cartas: ícones, nomes, subtítulos, ataques e importação por CSV."
)

criar_botao_painel(
    frame_sidebar,
    "Impressão",
    mostrar_tela_impressao,
    "🖨️",
    "Funções para preparar impressão: PDF, qualidade, corte, organização, exportação e texto vetorial."
)

criar_botao_painel(
    frame_sidebar,
    "Sistema",
    mostrar_tela_sistema,
    "⚙️",
    "Mostra informações do sistema e estrutura atual dos arquivos."
)


# ============================================================
# DESCRIÇÃO DINÂMICA
# ============================================================

descricao_var = tk.StringVar()
descricao_var.set(
    "Passe o mouse sobre uma opção para ver o que ela faz e quais arquivos ela espera."
)

frame_descricao = tk.Frame(
    frame_sidebar,
    bg="#181818",
    padx=12,
    pady=10
)

frame_descricao.pack(
    side="bottom",
    fill="x",
    padx=12,
    pady=(0, 12)
)

tk.Label(
    frame_descricao,
    text="Descrição",
    bg="#181818",
    fg=COR_DESTAQUE,
    font=("Arial", 10, "bold")
).pack(anchor="w")

tk.Label(
    frame_descricao,
    textvariable=descricao_var,
    bg="#181818",
    fg=COR_TEXTO_SEC,
    wraplength=180,
    justify="left",
    font=("Arial", 9)
).pack(anchor="w", pady=(4, 0))

tk.Label(
    frame_sidebar,
    text="v1.0",
    bg=COR_SIDEBAR,
    fg="#666666",
    font=("Arial", 9)
).pack(side="bottom", pady=(0, 12))


# ============================================================
# INICIAR
# ============================================================

mostrar_tela_inicio()
janela.mainloop()
