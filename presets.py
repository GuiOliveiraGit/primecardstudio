# ============================================================
# PRESETS VISUAIS DO SOFTWARE DE CARTAS
# ============================================================

PRESETS = {
    "Magic": {
        "nome": "Magic",
        "cor": "#7FC7FF",
        "estilo": "com_borda",
        "transparencia": 230,
        "alinhamento": "esquerda",
        "glow": False,
        "sombra_forte": False,
        "descricao": "Borda clássica, caixa sólida e visual inspirado em Magic."
    },

    "Minimalista": {
        "nome": "Minimalista",
        "cor": "#FFFFFF",
        "estilo": "sem_borda",
        "transparencia": 80,
        "alinhamento": "esquerda",
        "glow": False,
        "sombra_forte": False,
        "descricao": "Sem borda, fundo transparente e visual limpo."
    },

    "Stranger Things": {
        "nome": "Stranger Things",
        "cor": "#C30212",
        "estilo": "borda_fina",
        "transparencia": 145,
        "alinhamento": "centro",
        "glow": True,
        "sombra_forte": True,
        "descricao": "Glow vermelho, sombras fortes e borda neon."
    }
}


def obter_preset(nome_preset):
    """
    Retorna as configurações de um preset.
    """

    return PRESETS.get(nome_preset, PRESETS["Minimalista"])


def listar_presets():
    """
    Retorna a lista com os nomes dos presets disponíveis.
    """

    return list(PRESETS.keys())