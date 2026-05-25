# ============================================================
# TEMPLATES DE CARTAS
# ============================================================

TEMPLATES = {

    "Magic": {

        "nome": "Magic",

        "resolucao": (1024, 1536),

        "nome_y": 55,
        "nome_altura": 90,

        "subtitulo_y": 980,
        "subtitulo_altura": 70,

        "texto_y": 1060,

        "bordas_arredondadas": True,

        "fonte_nome": "beleren.ttf",
        "fonte_texto": "mplantin.ttf",

        "descricao": "Template estilo Magic clássico."
    },

    "Coup": {

        "nome": "Coup",

        "resolucao": (966, 1629),

        "nome_y": 70,
        "nome_altura": 110,

        "subtitulo_y": 1050,
        "subtitulo_altura": 85,

        "texto_y": 1140,

        "bordas_arredondadas": True,

        "fonte_nome": "TrajanPro-Bold.otf",
        "fonte_texto": "MinionPro-Regular.otf",

        "descricao": "Template estilo Coup."
    },

    "Pokemon": {

        "nome": "Pokemon",

        "resolucao": (745, 1040),

        "nome_y": 40,
        "nome_altura": 70,

        "subtitulo_y": 700,
        "subtitulo_altura": 60,

        "texto_y": 780,

        "bordas_arredondadas": True,

        "fonte_nome": "pokemon.ttf",
        "fonte_texto": "arial.ttf",

        "descricao": "Template estilo Pokémon."
    },

    "Hearthstone": {

        "nome": "Hearthstone",

        "resolucao": (800, 1100),

        "nome_y": 110,
        "nome_altura": 60,

        "subtitulo_y": 760,
        "subtitulo_altura": 55,

        "texto_y": 830,

        "bordas_arredondadas": True,

        "fonte_nome": "belwe.ttf",
        "fonte_texto": "frizqt.ttf",

        "descricao": "Template estilo Hearthstone."
    },

    "Customizado": {

        "nome": "Customizado",

        "resolucao": (1024, 1536),

        "nome_y": 60,
        "nome_altura": 90,

        "subtitulo_y": 980,
        "subtitulo_altura": 70,

        "texto_y": 1060,

        "bordas_arredondadas": True,

        "fonte_nome": "arial.ttf",
        "fonte_texto": "arial.ttf",

        "descricao": "Template livre editável."
    }
}


def listar_templates():

    return list(TEMPLATES.keys())


def obter_template(nome):

    return TEMPLATES.get(
        nome,
        TEMPLATES["Customizado"]
    )