---
name: coop-contribute
description: "Devolver o aprendizado ao coop-anything: atualizar o diretório, escrever o relato técnico do jogo, melhorar os guias e abrir uma pull request como rascunho após o usuário revisar as diferenças."
---

<a id="contribute-back"></a>
# Contribua de volta

1. Faça um fork e crie a branch `game/<slug>`.
2. Diretório: edite `data/directory.yaml` e execute `python tools/build_directory.py`.
3. Relato técnico: crie `games/<slug>/README.md` a partir de `templates/game.md`, com nível de QA e o que funciona (sem listas do que ainda não foi comprovado; pendências ficam em issues).
4. Guias: corrija ou amplie a página com orientações incorretas ou ausentes.
5. Limpeza: nenhuma informação pessoal, token, arquivo ou recurso de jogo. Código baseado em descompilação é bem-vindo; coloque o código completo de cada jogo no repositório próprio dele e acrescente o link.
6. Mostre as diferenças ao usuário e depois execute `gh pr create --draft` com o modelo preenchido.

Detalhes: `AGENTS.md`, `CONTRIBUTING.md`.
