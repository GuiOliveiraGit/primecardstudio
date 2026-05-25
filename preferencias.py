import json
import os

ARQUIVO_PREFERENCIAS = "preferencias.json"


def carregar_preferencias():
    if not os.path.exists(ARQUIVO_PREFERENCIAS):
        return {}

    try:
        with open(ARQUIVO_PREFERENCIAS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            if isinstance(dados, dict):
                return dados
    except Exception:
        return {}

    return {}


def salvar_preferencias(preferencias):
    with open(ARQUIVO_PREFERENCIAS, "w", encoding="utf-8") as arquivo:
        json.dump(preferencias, arquivo, ensure_ascii=False, indent=4)


def obter_preferencia(chave, padrao=None):
    return carregar_preferencias().get(chave, padrao)


def atualizar_preferencias(**valores):
    preferencias = carregar_preferencias()

    for chave, valor in valores.items():
        preferencias[chave] = valor

    salvar_preferencias(preferencias)
    return preferencias
