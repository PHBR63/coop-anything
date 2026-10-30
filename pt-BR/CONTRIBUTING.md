<a id="contributing"></a>
# Como contribuir

Pessoas e agentes seguem o mesmo fluxo. Agentes: [AGENTS.md](AGENTS.md) contém as regras completas; esta página é a versão resumida.

1. **Faça um fork** e crie a branch `game/<game-slug>` (ou `directory/<what>` para correções apenas no diretório).
2. **Diretório:** edite `data/directory.yaml` (esquema: [data/SCHEMA.md](data/SCHEMA.md)); depois execute `python tools/build_directory.py` e inclua o `DIRECTORY.md` regenerado no commit. Toda entrada precisa de um link de fonte e uma data em `checked`.
3. **Relatos técnicos:** crie `games/<game-slug>/README.md` a partir de [templates/game.md](templates/game.md). Mantenha notas brutas em `games/<game-slug>/NOTES.md` se forem úteis para a próxima pessoa.
4. **Guias:** corrija ou amplie uma página em `playbook/` quando uma técnica estiver ausente ou errada e informe qual jogo trouxe esse aprendizado.
5. **Abra a PR** com o modelo preenchido. Um jogo por PR.

Não faça o seguinte:

- Adicionar arquivos ou recursos de jogos (arte, áudio, ROMs, dados de jogo) nem links para baixá-los.
- Incluir aqui o código de um jogo inteiro: trabalhos baseados em descompilação são bem-vindos, mas ficam no repositório próprio do jogo, com um link a partir daqui.
- Colar informações pessoais (nomes, e-mails, nomes de usuário em caminhos, tokens, registros de conversas privadas).
- Declarar um nível de QA que você não alcançou. `unknown` e `untested` são respostas válidas.

Vai começar um jogo que ninguém está cobrindo? Abra primeiro uma issue **"claim a game"** para as pessoas poderem se encontrar. Encontrou um mod cooperativo que não está na lista? Basta preencher o formulário de issue **"new co-op project"**; o agente de alguém o transformará em uma entrada.
