import tkinter as tk
from tkinter import messagebox

from config import PRESETS_CARTA
from preferencias import carregar_preferencias, atualizar_preferencias


def abrir_configuracoes(janela_pai=None):
    preferencias = carregar_preferencias()
    janela = tk.Toplevel(janela_pai)
    janela.title("Configuracoes")
    janela.geometry("440x430")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(
        janela,
        text="Configuracoes de impressao",
        font=("Arial", 15, "bold")
    ).pack(pady=(18, 12))

    corpo = tk.Frame(janela)
    corpo.pack(fill="x", padx=24)

    preset_var = tk.StringVar(
        value=preferencias.get(
            "preset_pdf",
            "Magic / Poker (63 x 88 mm)"
        )
    )

    campos = {}

    def adicionar_campo(rotulo, chave, padrao):
        tk.Label(corpo, text=rotulo).pack(anchor="w", pady=(8, 0))
        entrada = tk.Entry(corpo)
        entrada.insert(0, str(preferencias.get(chave, padrao)))
        entrada.pack(fill="x")
        campos[chave] = entrada

    tk.Label(corpo, text="Preset padrao").pack(anchor="w")
    tk.OptionMenu(corpo, preset_var, *PRESETS_CARTA.keys()).pack(fill="x")

    preset_base = PRESETS_CARTA.get(preset_var.get(), PRESETS_CARTA["Personalizado"])

    adicionar_campo("Largura em mm", "largura_mm", preset_base["largura_mm"])
    adicionar_campo("Altura em mm", "altura_mm", preset_base["altura_mm"])
    adicionar_campo("Sangria em mm", "sangria_mm", preset_base["sangria_mm"])
    adicionar_campo(
        "Margem segura em mm",
        "margem_segura_mm",
        preset_base["margem_segura_mm"]
    )
    adicionar_campo(
        "Espacamento em mm",
        "espacamento_mm",
        preset_base["espacamento_mm"]
    )
    adicionar_campo("Quantidade padrao", "quantidade_pdf", 2)

    def salvar():
        try:
            valores = {
                "preset_pdf": preset_var.get(),
                "largura_mm": float(campos["largura_mm"].get()),
                "altura_mm": float(campos["altura_mm"].get()),
                "sangria_mm": float(campos["sangria_mm"].get()),
                "margem_segura_mm": float(campos["margem_segura_mm"].get()),
                "espacamento_mm": float(campos["espacamento_mm"].get()),
                "quantidade_pdf": int(campos["quantidade_pdf"].get())
            }
        except ValueError:
            messagebox.showerror(
                "Configuracoes",
                "Confira os numeros informados antes de salvar."
            )
            return

        atualizar_preferencias(**valores)
        messagebox.showinfo("Configuracoes", "Preferencias salvas.")
        janela.destroy()

    tk.Button(
        janela,
        text="Salvar configuracoes",
        width=24,
        command=salvar
    ).pack(pady=18)
