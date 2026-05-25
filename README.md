# PrimeStudio Card

PrimeStudio Card e um aplicativo em Python/Tkinter para criar, organizar e preparar cartas para impressao. Ele trabalha com imagens de cartas, metadados em JSON, exportacao profissional, preview e fechamento de PDF para grafica.

## Recursos principais

- Adicionar icones nas cartas com preview, tamanho e posicao configuraveis.
- Criar caixa de nome estilo Magic.
- Adicionar subtitulo, ataques e habilidades.
- Importar dados por CSV.
- Organizar cartas por metadados.
- Verificar qualidade de impressao.
- Fazer pre-checagem do projeto antes do PDF.
- Editar uma carta em uma tela central de metadados.
- Gerenciar projeto com nome, pasta de frentes, versos e saida.
- Configurar tamanho, sangria, margem segura, espacamento e quantidade padrao.
- Validar se o ambiente tem as dependencias instaladas.
- Gerar PDF A4 com frente, verso, sangria, margem segura e marcas de corte.
- Exportar PNG, TIFF, PDF, SVG simples e PDF vetorial.
- Acompanhar operacoes em lote com barra de progresso.
- Salvar backup automatico do `banco_cartas.json`.
- Lembrar preferencias recentes de PDF em `preferencias.json`.

## Instalar

Use Python 3.10 ou superior.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

Se o ambiente virtual `.qa_venv` existir, o atalho abaixo usa ele automaticamente. Se nao existir, tenta usar `.vendor_packages`:

```bash
run_app.bat
```

## Fluxo recomendado

1. Prepare as imagens das frentes em uma pasta.
2. Use `Criacao` para adicionar nomes, subtitulos, habilidades e icones.
3. Use `Importar Cartas por CSV` se quiser preencher muitos metadados de uma vez.
4. Use `Editor Central da Carta` para ajustar uma carta individual.
5. Use `Configuracoes de Impressao` para salvar medidas padrao.
6. Use `Pre-checagem do Projeto` antes de fechar o PDF.
7. Use `Gerar PDF para Recorte` para montar o arquivo A4 final.

## Projeto e configuracoes

Na tela `Sistema`, use:

- `Gerenciar Projeto` para salvar nome do projeto e pastas principais.
- `Configuracoes` para definir medidas padrao.
- `Validar Ambiente` para conferir Python, bibliotecas e empacotamento.

## Formatos aceitos

O app aceita imagens `.png`, `.jpg`, `.jpeg` e `.webp`.

## CSV

O importador espera um CSV separado por ponto e virgula (`;`). Campos uteis:

```csv
arquivo;nome;subtitulo;cor;estilo;quantidade;ataque1_nome;ataque1_descricao
demogorgon.png;Demogorgon;Criatura;#C30212;Minimalista;2;Investida;Causa dano extra.
```

## Gerar executavel Windows

Instale as dependencias de desenvolvimento:

```bash
python -m pip install -r requirements-dev.txt
```

Depois execute:

```bash
build_exe.bat
```

O executavel sera criado dentro de `dist\PrimeStudio Card\`.

## Arquivos de dados

- `banco_cartas.exemplo.json`: exemplo de banco para iniciar um projeto.
- `banco_cartas.json`: banco principal das cartas, criado localmente e ignorado pelo Git.
- `banco_cartas.backup.json`: backup automatico criado antes de salvar mudancas.
- `preferencias.json`: ultimas configuracoes usadas no PDF.

## Observacoes

PDF/X real ainda aparece como etapa futura no app. Por enquanto, use PDF normal, TIFF ou PDF vetorial conforme a necessidade da grafica.

No PDF Vetorial, a arte base da carta continua sendo uma imagem dentro do PDF. Os textos adicionados por cima sao vetoriais.
