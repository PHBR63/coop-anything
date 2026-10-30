---
name: coop-triage
description: "Começar por aqui para qualquer jogo. Identificar a compilação e o motor exatos, consultar o diretório coop-anything e os trabalhos existentes e escolher entre concluir um mod cooperativo existente ou criar do zero."
---

<a id="co-op-triage"></a>
# Triagem do modo cooperativo

1. Registre a identidade em `local/identity.md`: título, loja, versão ou identificador da compilação, SHA-256 do executável principal, motor e sistema operacional.
2. Procure o jogo em `DIRECTORY.md` e `games/`. Execute `gh issue list --search "<game>"` e `gh pr list --search "<game>"`.
3. Identifique o motor pela instalação (extensões dos arquivos, nomes de DLLs, informações de versão do executável). Consulte `playbook/engine-families.md` para jogos do mesmo motor com trabalho cooperativo.
4. Verifique quanto código-fonte existe: port de código aberto ou descompilação, scripts distribuídos com o jogo, extensão de scripts ou somente binário fechado.
5. Confira se o motor já possui código de rede multiplayer (um modo deathmatch indica que existe replicação).
6. Decida e informe ao usuário:
   - Mod existente com bugs ou abandonado: use a skill `coop-revive`.
   - Nada utilizável: use `coop-build-from-zero`.
7. Prepare para o usuário uma issue "claim a game" em rascunho.

Detalhes: `playbook/triage.md`.
