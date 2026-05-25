import json
import os
import shutil
from datetime import datetime

ARQUIVO_BANCO = "banco_cartas.json"
ARQUIVO_BACKUP = "banco_cartas.backup.json"


class BancoCartasErro(Exception):
    pass


# ============================================================
# BANCO
# ============================================================

def carregar_banco():

    if not os.path.exists(ARQUIVO_BANCO):
        return {}

    try:
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as arquivo:
            banco = json.load(arquivo)

    except json.JSONDecodeError as erro:
        raise BancoCartasErro(
            f"O arquivo {ARQUIVO_BANCO} esta corrompido: {erro}"
        ) from erro

    except OSError as erro:
        raise BancoCartasErro(
            f"Nao foi possivel ler {ARQUIVO_BANCO}: {erro}"
        ) from erro

    if not isinstance(banco, dict):
        raise BancoCartasErro(
            f"O arquivo {ARQUIVO_BANCO} precisa conter um objeto JSON."
        )

    return normalizar_banco(banco)


def salvar_banco(banco):
    criar_backup_banco()

    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as arquivo:
        json.dump(
            banco,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def criar_backup_banco():
    if not os.path.exists(ARQUIVO_BANCO):
        return

    try:
        shutil.copy2(ARQUIVO_BANCO, ARQUIVO_BACKUP)
    except Exception:
        pass


def normalizar_banco(banco):
    normalizado = {}

    for chave, carta in banco.items():
        nova_chave = normalizar_chave_texto(chave)

        if not isinstance(carta, dict):
            carta = {}

        carta.setdefault("arquivo", nova_chave)
        normalizado[nova_chave] = carta

    return normalizado


def normalizar_chave_texto(texto):
    return (
        str(texto)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_chave(nome_arquivo):

    nome = os.path.splitext(os.path.basename(nome_arquivo))[0]

    return normalizar_chave_texto(nome)


def nome_exibicao_padrao(nome_arquivo):

    chave = normalizar_chave(nome_arquivo)

    return chave.replace("_", " ").title()


# ============================================================
# ESTRUTURA PADRÃO DA CARTA
# ============================================================

def criar_carta_padrao(nome_arquivo):

    chave = normalizar_chave(nome_arquivo)

    return {
        "arquivo": chave,
        "nome": nome_exibicao_padrao(nome_arquivo),
        "subtitulo": "",
        "habilidades": [],
        "cor": "#FFFFFF",
        "estilo": "Minimalista",
        "preset": "Minimalista",
        "template": "Magic",
        "quantidade": 1,
        "raridade": "",
        "expansao": "",
        "ordem": 9999,
        "verso": "",
        "icone": "",
        "posicoes": {},
        "fontes": {},
        "pdf": {},
        "atualizado_em": data_atual()
    }


def data_atual():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# OBTER / GARANTIR CARTA
# ============================================================

def obter_carta(nome_arquivo):

    banco = carregar_banco()
    chave = normalizar_chave(nome_arquivo)

    return banco.get(chave, criar_carta_padrao(chave))


def garantir_carta(nome_arquivo):

    banco = carregar_banco()
    chave = normalizar_chave(nome_arquivo)

    if chave not in banco:
        banco[chave] = criar_carta_padrao(chave)
        salvar_banco(banco)

    return banco[chave]


# ============================================================
# SALVAR CARTA SEM APAGAR CAMPOS ANTIGOS
# ============================================================

def salvar_carta(
    nome_arquivo,
    nome=None,
    subtitulo=None,
    habilidades=None,
    cor=None,
    estilo=None,
    preset=None,
    template=None,
    quantidade=None,
    raridade=None,
    expansao=None,
    ordem=None,
    verso=None,
    icone=None,
    posicoes=None,
    fontes=None,
    pdf=None
):

    banco = carregar_banco()
    chave = normalizar_chave(nome_arquivo)

    if chave not in banco:
        banco[chave] = criar_carta_padrao(chave)

    carta = banco[chave]

    atualizar_se_nao_nulo(carta, "nome", nome)
    atualizar_se_nao_nulo(carta, "subtitulo", subtitulo)
    atualizar_se_nao_nulo(carta, "habilidades", habilidades)
    atualizar_se_nao_nulo(carta, "cor", cor)
    atualizar_se_nao_nulo(carta, "estilo", estilo)
    atualizar_se_nao_nulo(carta, "preset", preset)
    atualizar_se_nao_nulo(carta, "template", template)
    atualizar_se_nao_nulo(carta, "quantidade", quantidade)
    atualizar_se_nao_nulo(carta, "raridade", raridade)
    atualizar_se_nao_nulo(carta, "expansao", expansao)
    atualizar_se_nao_nulo(carta, "ordem", ordem)
    atualizar_se_nao_nulo(carta, "verso", verso)
    atualizar_se_nao_nulo(carta, "icone", icone)

    if posicoes is not None:
        carta["posicoes"] = mesclar_dicionario(
            carta.get("posicoes", {}),
            posicoes
        )

    if fontes is not None:
        carta["fontes"] = mesclar_dicionario(
            carta.get("fontes", {}),
            fontes
        )

    if pdf is not None:
        carta["pdf"] = mesclar_dicionario(
            carta.get("pdf", {}),
            pdf
        )

    carta["atualizado_em"] = data_atual()

    salvar_banco(banco)

    return carta


def atualizar_se_nao_nulo(dicionario, chave, valor):

    if valor is not None:
        dicionario[chave] = valor


def mesclar_dicionario(original, novo):

    resultado = original.copy()

    for chave, valor in novo.items():
        resultado[chave] = valor

    return resultado


# ============================================================
# CAMPOS ESPECÍFICOS
# ============================================================

def salvar_nome(nome_arquivo, nome):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        nome=nome
    )


def salvar_habilidades(
    nome_arquivo,
    subtitulo,
    habilidades,
    cor=None,
    estilo=None,
    preset=None,
    template=None,
    posicoes=None,
    fontes=None
):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        subtitulo=subtitulo,
        habilidades=habilidades,
        cor=cor,
        estilo=estilo,
        preset=preset,
        template=template,
        posicoes=posicoes,
        fontes=fontes
    )


def salvar_quantidade(nome_arquivo, quantidade):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        quantidade=quantidade
    )


def salvar_metadados(
    nome_arquivo,
    ordem=None,
    raridade=None,
    expansao=None
):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        ordem=ordem,
        raridade=raridade,
        expansao=expansao
    )


def salvar_icone(nome_arquivo, caminho_icone):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        icone=caminho_icone
    )


def salvar_verso(nome_arquivo, caminho_verso):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        verso=caminho_verso
    )


def salvar_config_pdf(nome_arquivo, configuracao_pdf):

    return salvar_carta(
        nome_arquivo=nome_arquivo,
        pdf=configuracao_pdf
    )


# ============================================================
# CONSULTAS
# ============================================================

def obter_valor(nome_arquivo, campo, padrao=None):

    carta = obter_carta(nome_arquivo)

    return carta.get(campo, padrao)


def listar_cartas():

    banco = carregar_banco()

    return banco


def listar_cartas_ordenadas():

    banco = carregar_banco()

    return dict(
        sorted(
            banco.items(),
            key=lambda item: item[1].get("ordem", 9999)
        )
    )


def buscar_por_expansao(expansao):

    banco = carregar_banco()

    resultado = {}

    for chave, carta in banco.items():
        if carta.get("expansao", "").lower() == expansao.lower():
            resultado[chave] = carta

    return resultado


def buscar_por_raridade(raridade):

    banco = carregar_banco()

    resultado = {}

    for chave, carta in banco.items():
        if carta.get("raridade", "").lower() == raridade.lower():
            resultado[chave] = carta

    return resultado
